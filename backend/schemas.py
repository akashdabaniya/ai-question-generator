"""Pydantic schemas for request validation and response serialization."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ── Request schemas ──────────────────────────────────────────────────────────

class QuestionGenerateRequest(BaseModel):
    """Payload for the POST /api/generate endpoint."""

    text: str = Field(
        ...,
        min_length=50,
        description="Source text from which questions will be generated (min 50 chars).",
    )
    topic: Optional[str] = Field(
        None,
        description="Optional topic label for the question set.",
    )
    difficulty: str = Field(
        "medium",
        pattern=r"^(easy|medium|hard)$",
        description="Difficulty level: easy, medium, or hard.",
    )
    num_questions: int = Field(
        5,
        ge=1,
        le=20,
        description="Number of questions to generate (1–20).",
    )
    question_types: List[str] = Field(
        default=["mcq", "true_false", "short_answer"],
        description="Types of questions to generate.",
    )


# ── Response schemas ─────────────────────────────────────────────────────────

class KeywordResponse(BaseModel):
    """A single extracted keyword with its relevance score."""

    keyword: str
    score: float


class QuestionResponse(BaseModel):
    """A single generated question."""

    id: str
    type: str
    question: str
    options: Optional[List[str]] = None
    answer: str
    explanation: Optional[str] = None
    difficulty: str


class GenerateResponse(BaseModel):
    """Response returned after generating questions."""

    session_id: str
    keywords: List[KeywordResponse]
    questions: List[QuestionResponse]
    metadata: Dict


class SessionSummary(BaseModel):
    """Lightweight representation for the history list."""

    id: str
    topic: Optional[str] = None
    input_preview: str
    question_count: int
    created_at: str


class SessionDetail(BaseModel):
    """Full session data including questions and keywords."""

    id: str
    input_text: str
    topic: Optional[str] = None
    difficulty: str
    keywords: List[KeywordResponse]
    questions: List[QuestionResponse]
    created_at: str
