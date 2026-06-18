"""SQLAlchemy ORM models for the AI Question Generator."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from database import Base


def _generate_uuid() -> str:
    """Generate a new UUID4 string for use as a primary key."""
    return str(uuid.uuid4())


class GenerationSession(Base):
    """Represents a single question-generation session.

    Stores the input text, extracted keywords, configuration, and links to
    all questions produced during this session.
    """

    __tablename__ = "generation_sessions"

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    input_text = Column(Text, nullable=False)
    topic = Column(String(255), nullable=True)
    difficulty = Column(String(50), default="medium", nullable=False)
    keywords = Column(JSON, nullable=True)  # stored as JSON list
    question_count = Column(Integer, nullable=False, default=0)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # One-to-many relationship with cascade delete
    questions = relationship(
        "GeneratedQuestion",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<GenerationSession id={self.id!r} topic={self.topic!r}>"


class GeneratedQuestion(Base):
    """A single question produced by the generator."""

    __tablename__ = "generated_questions"

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    session_id = Column(
        String(36),
        ForeignKey("generation_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_type = Column(String(50), nullable=False)  # mcq | true_false | short_answer
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # list of strings for MCQ, null otherwise
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(50), nullable=False, default="medium")
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Back-reference to the parent session
    session = relationship("GenerationSession", back_populates="questions")

    def __repr__(self) -> str:
        return f"<GeneratedQuestion id={self.id!r} type={self.question_type!r}>"
