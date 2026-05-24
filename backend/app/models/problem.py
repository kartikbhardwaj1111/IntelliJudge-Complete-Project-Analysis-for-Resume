"""
IntelliJudge — Problem Model

Maps to the "problems" table. A Problem is created when a user uploads a
screenshot and the AI reconstructs it into a structured coding problem.

RELATIONSHIPS:
  - Problem belongs to one User (user_id FK)
  - Problem has many TestCases (one-to-many)
  - Problem has many Submissions (one-to-many)

JSONB columns (constraints, examples, tags):
  PostgreSQL JSONB stores structured data (dicts/lists) natively with indexing.
  Much better than storing JSON as a string.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.submission import Submission
    from app.models.test_case import TestCase
    from app.models.user import User


class Problem(Base):
    """
    A reconstructed coding problem from an uploaded screenshot.
    """

    __tablename__ = "problems"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    input_format: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    output_format: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # JSONB: {"time": "1 second", "memory": "256 MB", "notes": "..."}
    constraints: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)

    # JSONB: [{"input": "...", "output": "...", "explanation": "..."}]
    examples: Mapped[Optional[List]] = mapped_column(JSONB, nullable=True)

    # "easy" | "medium" | "hard"
    difficulty: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, index=True
    )

    # JSONB: ["array", "sorting", "binary-search"]
    tags: Mapped[Optional[List]] = mapped_column(JSONB, nullable=True)

    # Raw text extracted by EasyOCR — kept for debugging / re-processing
    ocr_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Cloudinary CDN URL of the uploaded screenshot
    screenshot_url: Mapped[Optional[str]] = mapped_column(
        String(1000), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # ─── Relationships ─────────────────────────────────────────

    user: Mapped["User"] = relationship("User", back_populates="problems")

    test_cases: Mapped[List["TestCase"]] = relationship(
        "TestCase",
        back_populates="problem",
        cascade="all, delete-orphan",
        order_by="TestCase.created_at",
    )

    submissions: Mapped[List["Submission"]] = relationship(
        "Submission",
        back_populates="problem",
        cascade="all, delete-orphan",
        order_by="Submission.created_at.desc()",
    )

    def __repr__(self) -> str:
        return f"<Problem(id={self.id}, title={self.title!r}, difficulty={self.difficulty})>"
