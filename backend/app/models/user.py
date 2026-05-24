"""
IntelliJudge — User Model

Maps to the "users" table. Stores authentication credentials for registered users.

RELATIONSHIPS:
  - User has many Problems (they create)
  - User has many Submissions (they make)

PASSWORD SECURITY:
  We store `password_hash`, never the plain text password.
  Hashing happens in the auth service using bcrypt (Phase 3).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.problem import Problem
    from app.models.submission import Submission


class User(Base):
    """
    User account model — authentication and identity.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    # Bcrypt hash — NEVER store plain text passwords
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ─── Relationships ─────────────────────────────────────────

    problems: Mapped[List["Problem"]] = relationship(
        "Problem",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="Problem.created_at.desc()",
    )

    submissions: Mapped[List["Submission"]] = relationship(
        "Submission",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="Submission.created_at.desc()",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username!r}, email={self.email!r})>"
