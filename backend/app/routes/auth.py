"""
IntelliJudge — Authentication Routes

Endpoints:
  POST /api/auth/register  → Create account, returns JWT
  POST /api/auth/login     → Validate credentials, returns JWT
  GET  /api/auth/me        → Return current user profile (protected)

ROUTE LAYER RESPONSIBILITY:
  Routes are intentionally thin. They:
    1. Declare the HTTP method, path, and status code
    2. Accept the validated request body (Pydantic validates it)
    3. Call the service function (which contains the real logic)
    4. Wrap the result in our standard success_response format

  No business logic lives here — it all lives in auth_service.py.
  This separation makes the code easier to test and maintain.

DEPENDENCY INJECTION:
  FastAPI uses Depends() for two things here:
    - db: AsyncSession = Depends(get_db)
        → Creates a DB session for this request, auto-closes after
    - user: User = Depends(get_current_user)
        → Validates the Bearer token and returns the User object
        → If no token or invalid token: automatically returns 401
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, RegisterRequest, UserResponse
from app.services.auth_service import login_user, register_user
from app.utils.exceptions import success_response
from app.utils.jwt import get_current_user

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new account",
    description=(
        "Creates a new user account. Returns a JWT token you can use "
        "immediately — no separate login step needed after registering."
    ),
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register with email, username, and password.

    - **email**: Must be a valid email format, unique across all accounts
    - **username**: 3-30 characters, letters/numbers/underscores only, unique
    - **password**: At least 8 characters

    Returns a JWT access token and the new user profile.
    """
    result = await register_user(db, data)
    return success_response(
        data=result,
        message="Account created successfully",
    )


@router.post(
    "/login",
    summary="Login to your account",
    description="Validates your email and password. Returns a JWT token on success.",
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Login with your email and password.

    - **email**: The email you registered with
    - **password**: Your account password

    Returns a JWT access token. Store it and send it as:
    `Authorization: Bearer <token>` on all authenticated requests.
    """
    result = await login_user(db, data)
    return success_response(
        data=result,
        message="Login successful",
    )


@router.get(
    "/me",
    summary="Get current user profile",
    description="Returns the profile of the currently authenticated user. Requires a valid Bearer token.",
)
async def me(
    current_user: User = Depends(get_current_user),
):
    """
    Returns your account profile.

    Requires `Authorization: Bearer <token>` header.
    Returns 401 if the token is missing, expired, or invalid.
    """
    return success_response(
        data=UserResponse.model_validate(current_user),
        message="Profile retrieved successfully",
    )
