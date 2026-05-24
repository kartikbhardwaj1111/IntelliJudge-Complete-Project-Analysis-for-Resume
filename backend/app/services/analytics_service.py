"""
IntelliJudge — Analytics Service

All database queries for the analytics dashboard.
Every function accepts a user UUID and an open AsyncSession and returns plain dicts.

Functions:
  get_overview_stats(user_id, db)           → stats-card data + streak
  get_difficulty_breakdown(user_id, db)     → easy/medium/hard/unknown counts
  get_topic_stats(user_id, db)              → accuracy per tag (top 8)
  get_activity_trends(user_id, db, days)    → daily submission counts (area chart)
  get_submission_history(user_id, db, ...)  → paginated history with problem titles
  get_streak(user_id, db)                   → consecutive active-day count
"""

import math
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from sqlalchemy import Date, case, cast, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.problem import Problem
from app.models.submission import Submission as Sub


# ── Overview ──────────────────────────────────────────────────────────────────

async def get_overview_stats(user_id: Any, db: AsyncSession) -> Dict[str, Any]:
    """Return all data needed for the 5 summary stat cards."""
    total_problems = await db.scalar(
        select(func.count()).select_from(Problem).where(Problem.user_id == user_id)
    ) or 0

    row = (
        await db.execute(
            select(
                func.count().label("total"),
                func.sum(case((Sub.verdict == "AC", 1), else_=0)).label("accepted"),
                func.avg(
                    case((Sub.verdict == "AC", Sub.runtime_ms), else_=None)
                ).label("avg_runtime"),
            ).where(Sub.user_id == user_id)
        )
    ).one()

    total_subs   = row.total or 0
    accepted     = int(row.accepted or 0)
    avg_runtime  = float(row.avg_runtime) if row.avg_runtime is not None else None
    accept_rate  = round(accepted / total_subs, 4) if total_subs > 0 else 0.0

    solved = await db.scalar(
        select(func.count(distinct(Sub.problem_id))).where(
            Sub.user_id == user_id, Sub.verdict == "AC"
        )
    ) or 0

    streak = await get_streak(user_id, db)

    return {
        "total_problems":    total_problems,
        "total_submissions": total_subs,
        "solved_problems":   int(solved),
        "acceptance_rate":   accept_rate,
        "avg_runtime_ms":    avg_runtime,
        "current_streak":    streak,
    }


# ── Streak ────────────────────────────────────────────────────────────────────

async def get_streak(user_id: Any, db: AsyncSession) -> int:
    """
    Return the number of consecutive days (ending today or yesterday)
    on which the user made at least one submission.
    """
    rows = (
        await db.execute(
            select(distinct(cast(Sub.created_at, Date)))
            .where(Sub.user_id == user_id)
            .order_by(cast(Sub.created_at, Date).desc())
        )
    ).all()

    if not rows:
        return 0

    date_list = [r[0] for r in rows]
    today = datetime.now(timezone.utc).date()
    first = date_list[0]

    # Streak is dead if last activity is older than yesterday
    if first < today - timedelta(days=1):
        return 0

    streak = 1
    for i in range(1, len(date_list)):
        if date_list[i] == first - timedelta(days=i):
            streak += 1
        else:
            break

    return streak


# ── Difficulty Breakdown ──────────────────────────────────────────────────────

async def get_difficulty_breakdown(user_id: Any, db: AsyncSession) -> Dict[str, Any]:
    """Return problem count + solved count per difficulty level."""
    problems = (
        await db.execute(
            select(Problem.id, Problem.difficulty).where(Problem.user_id == user_id)
        )
    ).all()

    solved_ids = set(
        (
            await db.execute(
                select(distinct(Sub.problem_id)).where(
                    Sub.user_id == user_id, Sub.verdict == "AC"
                )
            )
        ).scalars().all()
    )

    buckets: dict = {
        "easy":    {"total": 0, "solved": 0},
        "medium":  {"total": 0, "solved": 0},
        "hard":    {"total": 0, "solved": 0},
        "unknown": {"total": 0, "solved": 0},
    }
    for pid, diff in problems:
        key = diff if diff in ("easy", "medium", "hard") else "unknown"
        buckets[key]["total"] += 1
        if pid in solved_ids:
            buckets[key]["solved"] += 1

    return buckets


# ── Topic / Tag Stats ─────────────────────────────────────────────────────────

async def get_topic_stats(user_id: Any, db: AsyncSession) -> Dict[str, Any]:
    """Return accuracy per tag — top 8 tags by problem count."""
    problems = (
        await db.execute(
            select(Problem.id, Problem.tags).where(Problem.user_id == user_id)
        )
    ).all()

    solved_ids = set(
        (
            await db.execute(
                select(distinct(Sub.problem_id)).where(
                    Sub.user_id == user_id, Sub.verdict == "AC"
                )
            )
        ).scalars().all()
    )

    tag_total: dict = {}
    tag_solved: dict = {}
    for pid, tags in problems:
        if not tags or not isinstance(tags, list):
            continue
        for raw_tag in tags:
            tag = str(raw_tag).lower().strip()
            if not tag:
                continue
            tag_total[tag] = tag_total.get(tag, 0) + 1
            if pid in solved_ids:
                tag_solved[tag] = tag_solved.get(tag, 0) + 1

    top = sorted(tag_total.items(), key=lambda x: x[1], reverse=True)[:8]
    return {
        "tags": [
            {
                "tag":      tag,
                "total":    total,
                "solved":   tag_solved.get(tag, 0),
                "accuracy": round(tag_solved.get(tag, 0) / total, 4) if total > 0 else 0.0,
            }
            for tag, total in top
        ]
    }


# ── Activity Trends ───────────────────────────────────────────────────────────

async def get_activity_trends(
    user_id: Any, db: AsyncSession, days: int = 30
) -> Dict[str, Any]:
    """Return daily submission + accepted counts for the last N days, zero-filled."""
    since = datetime.now(timezone.utc) - timedelta(days=days - 1)

    rows = (
        await db.execute(
            select(
                cast(Sub.created_at, Date).label("date"),
                func.count().label("submissions"),
                func.sum(case((Sub.verdict == "AC", 1), else_=0)).label("accepted"),
            )
            .where(Sub.user_id == user_id, Sub.created_at >= since)
            .group_by(cast(Sub.created_at, Date))
            .order_by(cast(Sub.created_at, Date))
        )
    ).all()

    data_map = {
        str(r.date): {"submissions": r.submissions, "accepted": int(r.accepted or 0)}
        for r in rows
    }

    daily = []
    for i in range(days):
        d = (since + timedelta(days=i)).date()
        date_str = str(d)
        entry = data_map.get(date_str, {"submissions": 0, "accepted": 0})
        daily.append({"date": date_str, **entry})

    return {"days": daily}


# ── Submission History ────────────────────────────────────────────────────────

async def get_submission_history(
    user_id: Any,
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    """Return paginated submission list with problem titles."""
    offset = (page - 1) * page_size

    total = await db.scalar(
        select(func.count()).select_from(Sub).where(Sub.user_id == user_id)
    ) or 0

    subs = (
        await db.execute(
            select(Sub)
            .options(selectinload(Sub.problem))
            .where(Sub.user_id == user_id)
            .order_by(Sub.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
    ).scalars().all()

    items = [
        {
            "id":                str(s.id),
            "problem_id":        str(s.problem_id),
            "problem_title":     s.problem.title if s.problem else "Deleted Problem",
            "language":          s.language,
            "verdict":           s.verdict,
            "test_cases_passed": s.test_cases_passed,
            "total_test_cases":  s.total_test_cases,
            "runtime_ms":        s.runtime_ms,
            "created_at":        s.created_at.isoformat(),
        }
        for s in subs
    ]

    return {
        "items": items,
        "total": total,
        "page":  page,
        "pages": math.ceil(total / page_size) if total > 0 else 1,
    }
