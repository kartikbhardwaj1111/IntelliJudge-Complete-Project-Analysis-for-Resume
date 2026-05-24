"""
Phase 10 — Analytics Routes

Thin HTTP layer — all query logic lives in analytics_service.py.

Endpoints (all require JWT, return only the requesting user's data):
  GET /api/analytics/overview              — 5 stat-card values + streak
  GET /api/analytics/difficulty            — difficulty distribution
  GET /api/analytics/topics  (+ /tags)     — tag accuracy (radar chart)
  GET /api/analytics/trends  (+ /activity) — 30-day daily submissions (area chart)
  GET /api/analytics/submissions           — paginated submission history
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.analytics_service import (
    get_activity_trends,
    get_difficulty_breakdown,
    get_overview_stats,
    get_submission_history,
    get_topic_stats,
)
from app.utils.exceptions import success_response
from app.utils.jwt import get_current_user

router = APIRouter()


@router.get("/overview")
async def overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return success_response(data=await get_overview_stats(current_user.id, db))


@router.get("/difficulty")
async def difficulty(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return success_response(data=await get_difficulty_breakdown(current_user.id, db))


@router.get("/topics")
async def topics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return success_response(data=await get_topic_stats(current_user.id, db))


@router.get("/tags")
async def tags(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Alias for /topics — kept for backwards compatibility."""
    return success_response(data=await get_topic_stats(current_user.id, db))


@router.get("/trends")
async def trends(
    days: int = Query(default=30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return success_response(data=await get_activity_trends(current_user.id, db, days=days))


@router.get("/activity")
async def activity(
    days: int = Query(default=30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Alias for /trends — kept for backwards compatibility."""
    return success_response(data=await get_activity_trends(current_user.id, db, days=days))


@router.get("/submissions")
async def submissions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return success_response(
        data=await get_submission_history(current_user.id, db, page=page, page_size=page_size)
    )
