"""
Phase 9 — AI Smart Features

Endpoints (all require valid JWT):
  POST /api/ai/feedback    — explain why code got WA / RE / TLE / CE
  POST /api/ai/hints       — progressive hints (level 1 → 2 → 3)
  POST /api/ai/edge-cases  — identify tricky edge cases to watch for

Rate limiting: 5 AI requests per user per endpoint per minute (in-memory,
  resets on server restart — suitable for a learning project).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.problem import Problem
from app.models.user import User
from app.schemas.ai import (
    EdgeCasesRequest,
    FeedbackRequest,
    HintRequest,
)
from app.services.ai_service import detect_edge_cases, generate_feedback, generate_hint
from app.utils.exceptions import NotFoundException, success_response
from app.utils.jwt import get_current_user
from app.utils.rate_limiter import ai_rate_limiter

router = APIRouter()


async def _fetch_problem(problem_id: str, db: AsyncSession) -> Problem:
    problem = await db.get(Problem, problem_id)
    if not problem:
        raise NotFoundException("Problem")
    return problem


@router.post("/feedback")
async def get_feedback(
    body: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Explain why submitted code received a non-AC verdict."""
    ai_rate_limiter.check(str(current_user.id), "feedback")
    problem = await _fetch_problem(body.problem_id, db)
    result = await generate_feedback(
        problem=problem,
        code=body.code,
        language=body.language,
        verdict=body.verdict,
        failing_input=body.failing_input,
        failing_expected=body.failing_expected,
        failing_actual=body.failing_actual,
    )
    return success_response(data=result, message="Feedback generated")


@router.post("/hints")
async def get_hint(
    body: HintRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a single progressive hint at the requested level (1, 2, or 3)."""
    ai_rate_limiter.check(str(current_user.id), "hints")
    problem = await _fetch_problem(body.problem_id, db)
    result = await generate_hint(
        problem=problem,
        code=body.code,
        language=body.language,
        hint_level=body.hint_level,
    )
    return success_response(data=result, message="Hint generated")


@router.post("/edge-cases")
async def get_edge_cases(
    body: EdgeCasesRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Identify tricky edge cases for a problem that beginners commonly miss."""
    ai_rate_limiter.check(str(current_user.id), "edge-cases")
    problem = await _fetch_problem(body.problem_id, db)
    result = await detect_edge_cases(problem)
    return success_response(data=result, message="Edge cases detected")
