"""API router for question generation, history, and export endpoints."""

import asyncio
import json
import time
import uuid
from io import BytesIO
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import GeneratedQuestion, GenerationSession
from schemas import (
    GenerateResponse,
    KeywordResponse,
    QuestionGenerateRequest,
    QuestionResponse,
    SessionDetail,
    SessionSummary,
)
from services.nlp_pipeline import KeywordExtractor
from services.question_generator import QuestionGenerator

router = APIRouter(prefix="/api", tags=["questions"])


# ── POST /api/generate ──────────────────────────────────────────────────────


@router.post("/generate", response_model=GenerateResponse)
async def generate_questions(
    request: QuestionGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Extract keywords and generate questions from the provided text."""
    start = time.perf_counter()

    # Run CPU-bound NLP work off the event loop
    extractor = KeywordExtractor.get_instance()
    keywords = await asyncio.to_thread(
        extractor.extract_keywords,
        request.text,
        top_n=10,
    )

    generator = QuestionGenerator.get_instance()
    raw_questions = await asyncio.to_thread(
        generator.generate,
        request.text,
        keywords,
        num_questions=request.num_questions,
        question_types=request.question_types,
        difficulty=request.difficulty,
    )

    # Persist session
    session_id = str(uuid.uuid4())
    session = GenerationSession(
        id=session_id,
        input_text=request.text,
        topic=request.topic,
        difficulty=request.difficulty,
        keywords=[{"keyword": k["keyword"], "score": k["score"]} for k in keywords],
        question_count=len(raw_questions),
    )
    db.add(session)

    # Persist questions
    question_responses: List[QuestionResponse] = []
    for q in raw_questions:
        q_id = str(uuid.uuid4())
        db_question = GeneratedQuestion(
            id=q_id,
            session_id=session_id,
            question_type=q["type"],
            question_text=q["question"],
            options=q.get("options"),
            correct_answer=q["answer"],
            explanation=q.get("explanation"),
            difficulty=q.get("difficulty", request.difficulty),
        )
        db.add(db_question)

        question_responses.append(
            QuestionResponse(
                id=q_id,
                type=q["type"],
                question=q["question"],
                options=q.get("options"),
                answer=q["answer"],
                explanation=q.get("explanation"),
                difficulty=q.get("difficulty", request.difficulty),
            )
        )

    await db.flush()

    elapsed = round(time.perf_counter() - start, 3)

    return GenerateResponse(
        session_id=session_id,
        keywords=[KeywordResponse(**k) for k in keywords],
        questions=question_responses,
        metadata={
            "total": len(question_responses),
            "processing_time": elapsed,
            "difficulty": request.difficulty,
            "question_types": request.question_types,
        },
    )


# ── GET /api/history ────────────────────────────────────────────────────────


@router.get("/history", response_model=List[SessionSummary])
async def get_history(db: AsyncSession = Depends(get_db)):
    """Return all past generation sessions, most recent first."""
    result = await db.execute(
        select(GenerationSession).order_by(GenerationSession.created_at.desc())
    )
    sessions = result.scalars().all()

    return [
        SessionSummary(
            id=s.id,
            topic=s.topic,
            input_preview=s.input_text[:150],
            question_count=s.question_count,
            created_at=s.created_at.isoformat() if s.created_at else "",
        )
        for s in sessions
    ]


# ── GET /api/history/{session_id} ──────────────────────────────────────────


@router.get("/history/{session_id}", response_model=SessionDetail)
async def get_session_detail(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return full details for a single session including all questions."""
    result = await db.execute(
        select(GenerationSession)
        .options(selectinload(GenerationSession.questions))
        .where(GenerationSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    keyword_list = session.keywords or []

    return SessionDetail(
        id=session.id,
        input_text=session.input_text,
        topic=session.topic,
        difficulty=session.difficulty,
        keywords=[KeywordResponse(**k) for k in keyword_list],
        questions=[
            QuestionResponse(
                id=q.id,
                type=q.question_type,
                question=q.question_text,
                options=q.options,
                answer=q.correct_answer,
                explanation=q.explanation,
                difficulty=q.difficulty,
            )
            for q in session.questions
        ],
        created_at=session.created_at.isoformat() if session.created_at else "",
    )


# ── DELETE /api/history/{session_id} ───────────────────────────────────────


@router.delete("/history/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a session and its cascaded questions."""
    result = await db.execute(
        select(GenerationSession).where(GenerationSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    await db.delete(session)
    await db.flush()

    return {"message": "Session deleted successfully", "session_id": session_id}


# ── GET /api/export/{session_id} ──────────────────────────────────────────


@router.get("/export/{session_id}")
async def export_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Export a session as a downloadable JSON file."""
    result = await db.execute(
        select(GenerationSession)
        .options(selectinload(GenerationSession.questions))
        .where(GenerationSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    export_data = {
        "session_id": session.id,
        "topic": session.topic,
        "difficulty": session.difficulty,
        "input_text": session.input_text,
        "keywords": session.keywords or [],
        "questions": [
            {
                "id": q.id,
                "type": q.question_type,
                "question": q.question_text,
                "options": q.options,
                "answer": q.correct_answer,
                "explanation": q.explanation,
                "difficulty": q.difficulty,
            }
            for q in session.questions
        ],
        "created_at": session.created_at.isoformat() if session.created_at else "",
    }

    content = json.dumps(export_data, indent=2, ensure_ascii=False).encode("utf-8")
    buffer = BytesIO(content)
    filename = f"questions_{session_id[:8]}.json"

    return StreamingResponse(
        buffer,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
