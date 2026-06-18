"""FastAPI application entry point for the AI Question Generator."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db
from routers import questions


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    # ── Startup ──────────────────────────────────────────────────────────
    await init_db()

    # Pre-load ML models in a background thread to keep the event loop free
    from services.nlp_pipeline import KeywordExtractor
    from services.question_generator import QuestionGenerator

    await asyncio.to_thread(KeywordExtractor.get_instance)
    await asyncio.to_thread(QuestionGenerator.get_instance)
    print("AI models loaded and ready!")

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────
    print("Shutting down...")


app = FastAPI(
    title="AI Question Generator",
    description="Generate intelligent questions from any text using NLP",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router)


@app.get("/api/health")
async def health_check():
    """Simple liveness probe."""
    return {"status": "healthy", "service": "AI Question Generator"}
