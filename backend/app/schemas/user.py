"""
IntelliJudge — User Pydantic Schemas

Schemas serve two purposes:
  1. INPUT validation — FastAPI uses them to validate and parse request bodies.
     If the client sends bad data, FastAPI automatically returns a 422 error
     with field-level details before your route code even runs.

  2. OUTPUT serialization — response schemas control exactly what gets sent back.
     This prevents accidentally leaking sensitive fields like password_hash.

PYDANTIC V2 KEY CONCEPTS:
  - EmailStr           → validates that a string is a real email format
  - Field(min_length=) → sets validation constraints with error messages
  - pattern=           → regex must match (username: letters, numbers, underscore only)
  - model_validate()   → converts a SQLAlchemy model instance into this schema
  - from_attributes=True → lets Pydantic read from ORM object attributes (not just dicts)
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ─── Request Schemas (incoming data from the client) ──────────


class RegisterRequest(BaseModel):
    """
    Body for POST /api/auth/register.

    Validation rules:
      email    → must be a valid email format
      username → 3-30 chars, only letters / numbers / underscore
      password → at least 8 characters
    """

    email: EmailStr

    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="3-30 characters: letters, numbers, and underscores only",
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="At least 8 characters",
    )


class LoginRequest(BaseModel):
    """
    Body for POST /api/auth/login.
    """

    email: EmailStr
    password: str


# ─── Response Schemas (outgoing data sent to the client) ───────


class UserResponse(BaseModel):
    """
    Safe user data to return in API responses.

    IMPORTANT: password_hash is intentionally NOT included here.
    Never expose password hashes or any credential data in responses.
    """

    id: uuid.UUID
    email: str
    username: str
    created_at: datetime
    updated_at: datetime

    # from_attributes=True lets Pydantic read from SQLAlchemy model instances.
    # Without this, model_validate(user_orm_object) would fail.
    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    """
    Returned by /register and /login.

    The client should:
      1. Store token in localStorage (or a secure cookie)
      2. Send it on every subsequent request:
           Authorization: Bearer <token>
    """

    token: str
    token_type: str = "bearer"
    user: UserResponse
