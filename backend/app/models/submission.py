"""
IntelliJudge — Submission Model

Maps to the "submissions" table. A Submission is created when a user runs
or submits code against a Problem through the Monaco editor.

VERDICT VALUES (competitive programming standard):
  "pending" → just created, Judge0 hasn't finished yet
  "AC"      → Accepted — all test cases passed
  "WA"      → Wrong Answer — output mismatch
  "TLE"     → Time Limit Exceeded
  "MLE"     → Memory Limit Exceeded
  "RE"      → Runtime Error (crash, segfault, unhandled exception)
  "CE"      → Compilation Error

LANGUAGE VALUES (maps to Judge0 language IDs):
  "cpp"        → C++17  (Judge0 ID: 54)
  "java"       → Java 17 (Judge0 ID: 62)
  "python"     → Python 3 (Judge0 ID: 71)
  "javascript" → Node.js (Judge0 ID: 63)

results JSONB structure:
  [
    {
      "test_case_id": "uuid",
      "verdict": "AC",
      "runtime_ms": 12,
      "memory_kb": 2048,
      "actual_output": "...",
      "expected_output": "..."
    },
    ...
  ]
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.problem import Problem
    from app.models.user import User


class Submission(Base):
    """
    A code submission made by a user for a specific problem.
    """

    __tablename__ = "submissions"

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

    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # "cpp" | "java" | "python" | "javascript"
    language: Mapped[str] = mapped_column(String(50), nullable=False)

    # The full source code submitted by the user
    code: Mapped[str] = mapped_column(Text, nullable=False)

    # Final verdict — starts as "pending", updated after Judge0 finishes
    verdict: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
        index=True,
    )

    # Execution stats — null until Judge0 returns results
    runtime_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    memory_kb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Summary counts
    test_cases_passed: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    total_test_cases: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    # Per-test-case breakdown stored as JSONB (see module docstring for shape)
    results: Mapped[Optional[List]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # ─── Relationships ─────────────────────────────────────────

    user: Mapped["User"] = relationship("User", back_populates="submissions")
    problem: Mapped["Problem"] = relationship("Problem", back_populates="submissions")

    def __repr__(self) -> str:
        return (
            f"<Submission(id={self.id}, verdict={self.verdict!r}, "
            f"language={self.language!r}, passed={self.test_cases_passed}/{self.total_test_cases})>"
        )
