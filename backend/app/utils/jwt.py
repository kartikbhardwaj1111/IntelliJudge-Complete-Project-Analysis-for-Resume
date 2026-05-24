"""
IntelliJudge — JWT Utilities + Auth Dependency

WHAT IS A JWT?
  JSON Web Token — a self-contained, signed token that proves identity.

  Structure: header.payload.signature
    header    → {"alg": "HS256", "typ": "JWT"}
    payload   → {"sub": "user-uuid", "email": "...", "exp": 1234567890}
    signature → HMAC-SHA256(header + payload, secret_key)

  Because only the server knows JWT_SECRET, no one can forge a valid token.
  No database lookup needed to validate — just verify the signature.

FLOW:
  1. User logs in → server creates token with create_access_token()
  2. Client stores token (localStorage / cookie)
  3. Client sends "Authorization: Bearer <token>" on every request
  4. Protected routes call Depends(get_current_user) which:
       a) Extracts the token from the Authorization header
       b) Decodes + validates it with our JWT_SECRET
       c) Fetches the User from the database
       d) Returns the User object to the route handler

EXPIRY:
  Tokens expire after JWT_EXPIRY_HOURS (default: 24 hours).
  After expiry the client must log in again to get a new token.
"""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.utils.exceptions import UnauthorizedException


class _BearerScheme(HTTPBearer):
    """
    Overrides HTTPBearer so a missing/invalid Authorization header returns
    401 (Unauthorized) instead of FastAPI's default 403 (Forbidden).
    """

    async def __call__(self, request: Request):  # type: ignore[override]
        from fastapi import HTTPException

        try:
            return await super().__call__(request)
        except HTTPException:
            raise UnauthorizedException(
                "Authentication required — send 'Authorization: Bearer <token>'"
            )


# FastAPI security scheme — tells Swagger UI to show the "Authorize" button
# and to send "Authorization: Bearer <token>" headers automatically.
bearer_scheme = _BearerScheme()


def create_access_token(user_id: str, username: str, email: str) -> str:
    """
    Create a signed JWT access token for the given user.

    The token encodes the user's ID, username, and email, plus an expiry time.
    Sign it with JWT_SECRET so only this server can validate it.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=settings.JWT_EXPIRY_HOURS)

    payload = {
        "sub": str(user_id),       # Subject — the user's UUID (as string)
        "username": username,
        "email": email,
        "iat": now,                # Issued at
        "exp": expire,             # Expiry
    }

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT token string.

    Raises UnauthorizedException (401) if the token is:
      - expired
      - tampered with / invalid signature
      - malformed
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except ExpiredSignatureError:
        raise UnauthorizedException("Token has expired — please log in again")
    except JWTError:
        raise UnauthorizedException("Invalid token — please log in again")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    FastAPI dependency — validates the Bearer token and returns the User.

    Add this to any route that requires authentication:
        @router.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"hello": user.username}

    What this does:
      1. Extracts the token from the "Authorization: Bearer <token>" header
      2. Decodes and validates the JWT signature + expiry
      3. Reads user_id from the token payload
      4. Fetches the User row from the database
      5. Returns the User object (or raises 401 if anything fails)
    """
    from app.models.user import User

    payload = decode_access_token(credentials.credentials)

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Invalid token — missing user identifier")

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException("Invalid token — malformed user identifier")

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()

    if not user:
        # Token was valid but the user was deleted after it was issued
        raise UnauthorizedException("User no longer exists")

    return user
