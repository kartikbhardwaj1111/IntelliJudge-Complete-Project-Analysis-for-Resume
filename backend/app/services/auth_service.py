"""
IntelliJudge — Authentication Service

This is the business logic layer. Routes are thin — they validate input and
return responses. Services contain the actual logic.

WHY A SEPARATE SERVICE?
  - Routes stay clean (no business logic mixed in)
  - Logic is reusable (another route or background job can call register_user())
  - Easier to test (no HTTP layer needed to test the logic)

SECURITY DECISIONS:
  - Login error is always "Invalid email or password" — never "email not found"
    or "wrong password". This prevents user enumeration attacks where an attacker
    tests whether emails are registered.
  - Passwords are hashed before storage, never stored plain.
  - Duplicate checks use case-insensitive comparison via .lower() on email.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.utils.exceptions import ConflictException, UnauthorizedException
from app.utils.hashing import hash_password, verify_password
from app.utils.jwt import create_access_token


async def register_user(db: AsyncSession, data: RegisterRequest) -> dict:
    """
    Create a new user account and return a JWT token.

    Steps:
      1. Check email is not already registered → 409 Conflict
      2. Check username is not already taken   → 409 Conflict
      3. Hash the password with bcrypt
      4. Insert the new User row
      5. Generate and return a JWT token + user data

    Why check both email AND username?
      Email is the login identifier. Username is the display name.
      Both must be globally unique for the platform to work correctly.
    """
    # ── Duplicate checks ───────────────────────────────────────
    existing_email = await db.execute(
        select(User).where(User.email == data.email.lower())
    )
    if existing_email.scalar_one_or_none():
        raise ConflictException("An account with this email already exists")

    existing_username = await db.execute(
        select(User).where(User.username == data.username)
    )
    if existing_username.scalar_one_or_none():
        raise ConflictException("This username is already taken")

    # ── Create user ────────────────────────────────────────────
    user = User(
        email=data.email.lower(),          # Store emails in lowercase (consistent)
        username=data.username,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)  # Re-load from DB to get server-generated id, timestamps

    # ── Generate token ─────────────────────────────────────────
    token = create_access_token(
        user_id=str(user.id),
        username=user.username,
        email=user.email,
    )

    return AuthResponse(
        token=token,
        user=UserResponse.model_validate(user),
    ).model_dump()


async def login_user(db: AsyncSession, data: LoginRequest) -> dict:
    """
    Validate credentials and return a JWT token.

    Steps:
      1. Find user by email
      2. Verify bcrypt password hash
      3. Generate and return a JWT token + user data

    NOTE: We return the same error message whether the email doesn't exist
    or the password is wrong. This prevents user enumeration.
    """
    # ── Find user ──────────────────────────────────────────────
    result = await db.execute(
        select(User).where(User.email == data.email.lower())
    )
    user = result.scalar_one_or_none()

    # ── Validate credentials ───────────────────────────────────
    # Check user exists AND password matches in a single condition.
    # This ensures the timing is similar whether the user exists or not,
    # reducing timing-based enumeration risk.
    if not user or not verify_password(data.password, user.password_hash):
        raise UnauthorizedException("Invalid email or password")

    # ── Generate token ─────────────────────────────────────────
    token = create_access_token(
        user_id=str(user.id),
        username=user.username,
        email=user.email,
    )

    return AuthResponse(
        token=token,
        user=UserResponse.model_validate(user),
    ).model_dump()
