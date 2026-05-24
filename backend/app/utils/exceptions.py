"""
IntelliJudge — Standard API Response Utilities

Every API response from IntelliJudge follows a consistent format:

SUCCESS:
{
    "success": true,
    "message": "Operation completed",
    "data": { ... }
}

ERROR:
{
    "success": false,
    "message": "Something went wrong",
    "data": null,
    "errors": [{"field": "email", "message": "Invalid format"}]
}

WHY?
  - Frontend always knows where to find data (response.data)
  - Frontend always knows if it succeeded (response.success)
  - Consistent error structure makes error handling simple
  - No guessing — every endpoint returns the same shape
"""

from typing import Any, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel


# ─── Response Models ───────────────────────────────────────────

class ErrorDetail(BaseModel):
    """A single field-level error."""
    field: str
    message: str


class ApiResponse(BaseModel):
    """Standard response wrapper for all API endpoints."""
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[list[ErrorDetail]] = None


# ─── Helper Functions ──────────────────────────────────────────

def success_response(
    data: Any = None,
    message: str = "Operation successful",
    status_code: int = status.HTTP_200_OK,
) -> dict:
    """
    Create a standard success response.
    
    Usage in a route:
        return success_response(data={"user": user}, message="User created")
    """
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(
    message: str = "An error occurred",
    errors: Optional[list[dict]] = None,
) -> dict:
    """
    Create a standard error response.
    
    Usage in a route:
        return error_response(message="Not found", errors=[...])
    """
    return {
        "success": False,
        "message": message,
        "data": None,
        "errors": errors,
    }


# ─── Custom Exceptions ────────────────────────────────────────

class AppException(HTTPException):
    """
    Base exception for all IntelliJudge errors.
    
    Extends FastAPI's HTTPException so it's automatically caught
    and returned as a proper HTTP response.
    
    Usage:
        raise AppException(
            status_code=404,
            message="Problem not found"
        )
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        errors: Optional[list[dict]] = None,
    ):
        self.message = message
        self.errors = errors
        super().__init__(status_code=status_code, detail=message)


class NotFoundException(AppException):
    """Raise when a requested resource doesn't exist (404)."""

    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"{resource} not found",
        )


class UnauthorizedException(AppException):
    """Raise when auth credentials are missing or invalid (401)."""

    def __init__(self, message: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
        )


class ConflictException(AppException):
    """Raise when a resource already exists — e.g. duplicate email (409)."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
        )


class BadRequestException(AppException):
    """Raise for invalid input that Pydantic didn't catch (400)."""

    def __init__(self, message: str = "Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
        )
