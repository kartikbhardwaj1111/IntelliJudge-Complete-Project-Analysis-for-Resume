"""
IntelliJudge — Problem Routes

All endpoints are auth-protected. Users can only access their own problems.

Endpoints:
  POST   /api/problems/reconstruct           AI-reconstruct OCR text into a structured problem
  GET    /api/problems                       List the current user's problems (paginated)
  GET    /api/problems/{id}                  Get full problem detail with visible test cases
  PUT    /api/problems/{id}                  Edit any field (correct AI output)
  DELETE /api/problems/{id}                  Delete problem and all its test cases + submissions

  POST   /api/problems/{id}/generate-tests   AI-generate test cases for a problem
  GET    /api/problems/{id}/test-cases       List all test cases (owner sees hidden too)
  POST   /api/problems/{id}/test-cases       Add a manual test case
  DELETE /api/problems/{id}/test-cases/{tc_id}  Delete one test case

ROUTE LAYER CONTRACT:
  - Routes validate inputs via Pydantic schemas (FastAPI handles it automatically).
  - All DB queries use the pattern: select → check ownership → 404 if missing.
  - Business logic (AI calls, test case formatting) lives in services — never in routes.
  - Every success response uses success_response() for consistent API shape.
"""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.problem import Problem
from app.models.test_case import TestCase
from app.models.user import User
from app.schemas.problem import (
    GenerateTestsRequest,
    ProblemCreate,
    ProblemListItem,
    ProblemResponse,
    ProblemUpdate,
    ReconstructRequest,
    TestCaseCreate,
    TestCaseResponse,
)
from app.services.ai_service import generate_test_cases, reconstruct_problem
from app.utils.exceptions import BadRequestException, NotFoundException, success_response
from app.utils.jwt import get_current_user

router = APIRouter()


# ─── Ownership guard ───────────────────────────────────────────
# Centralised helper so every route gets consistent ownership enforcement.

async def _get_owned_problem(
    problem_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
    load_test_cases: bool = False,
) -> Problem:
    """
    Fetch a Problem by ID, asserting it belongs to current_user.
    Raises NotFoundException (404) if missing or owned by someone else.
    """
    query = select(Problem).where(
        Problem.id == problem_id,
        Problem.user_id == current_user.id,
    )
    if load_test_cases:
        query = query.options(selectinload(Problem.test_cases))

    result = await db.execute(query)
    problem = result.scalar_one_or_none()
    if not problem:
        raise NotFoundException("Problem")
    return problem


# ══════════════════════════════════════════════════════════════
# POST /api/problems/reconstruct
# ══════════════════════════════════════════════════════════════

@router.post(
    "/reconstruct",
    status_code=status.HTTP_200_OK,
    summary="AI-reconstruct a problem from OCR text",
    description=(
        "Sends the stored OCR text (or an override) to Google Gemini and updates "
        "the Problem with the reconstructed title, description, examples, "
        "constraints, difficulty, and tags. "
        "Call this after POST /api/upload/screenshot."
    ),
)
async def reconstruct(
    data: ReconstructRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Full AI reconstruction flow:
      1. Load the partial Problem created by the upload step
      2. Decide which OCR text to use (stored vs. override)
      3. Call Gemini → get structured JSON
      4. Persist all reconstructed fields back to the Problem row
      5. Return the fully populated ProblemResponse

    Gemini is called in a thread pool so the event loop stays unblocked.
    Expect 3-10 seconds depending on problem length and API latency.
    """
    problem = await _get_owned_problem(data.problem_id, current_user, db, load_test_cases=True)

    # Decide which text to send to Gemini
    ocr_text = data.ocr_text_override or problem.ocr_text
    if not ocr_text or not ocr_text.strip():
        raise BadRequestException(
            "No OCR text available for this problem. "
            "Upload a screenshot first (POST /api/upload/screenshot) "
            "or provide ocr_text_override in the request body."
        )

    # AI call (3-10s typical)
    reconstructed = await reconstruct_problem(ocr_text)

    # Persist reconstruction results
    problem.title = reconstructed["title"]
    problem.description = reconstructed["description"]
    problem.input_format = reconstructed["input_format"]
    problem.output_format = reconstructed["output_format"]
    problem.constraints = reconstructed["constraints"]
    problem.examples = reconstructed["examples"]
    problem.difficulty = reconstructed["difficulty"]
    problem.tags = reconstructed["tags"]

    await db.commit()
    await db.refresh(problem)

    # Reload with test cases (empty at this point, but consistent with the response schema)
    result = await db.execute(
        select(Problem)
        .where(Problem.id == problem.id)
        .options(selectinload(Problem.test_cases))
    )
    problem = result.scalar_one()

    return success_response(
        data=ProblemResponse.model_validate(problem).model_dump(),
        message="Problem reconstructed successfully",
    )


# ══════════════════════════════════════════════════════════════
# GET /api/problems  — paginated list
# ══════════════════════════════════════════════════════════════

@router.get(
    "",
    summary="List your problems",
    description=(
        "Returns a paginated list of the current user's problems. "
        "Use `difficulty`, `tag`, and `search` to filter. "
        "Each item is a lightweight card — fetch /api/problems/{id} for full details."
    ),
)
async def list_problems(
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Results per page"),
    difficulty: Optional[str] = Query(default=None, description="Filter by difficulty: easy | medium | hard"),
    tag: Optional[str] = Query(default=None, description="Filter problems that include this tag"),
    search: Optional[str] = Query(default=None, description="Full-text search on title"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns lightweight ProblemListItem cards, sorted by newest first.
    Each card includes the test case count (counted server-side).
    """
    query = select(Problem).where(Problem.user_id == current_user.id)

    if difficulty:
        query = query.where(Problem.difficulty == difficulty.lower())
    if search:
        query = query.where(Problem.title.ilike(f"%{search}%"))
    if tag:
        # JSONB array containment: tags @> '["arrays"]'
        query = query.where(Problem.tags.contains([tag.lower()]))

    query = query.order_by(Problem.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    problems = result.scalars().all()

    # Count test cases per problem in one query
    if problems:
        problem_ids = [p.id for p in problems]
        tc_counts_result = await db.execute(
            select(TestCase.problem_id, func.count(TestCase.id).label("cnt"))
            .where(TestCase.problem_id.in_(problem_ids))
            .group_by(TestCase.problem_id)
        )
        tc_map = {row.problem_id: row.cnt for row in tc_counts_result}
    else:
        tc_map = {}

    items = []
    for p in problems:
        item = ProblemListItem(
            id=p.id,
            title=p.title,
            difficulty=p.difficulty,
            tags=p.tags,
            screenshot_url=p.screenshot_url,
            created_at=p.created_at,
            test_case_count=tc_map.get(p.id, 0),
        )
        items.append(item.model_dump())

    return success_response(
        data={
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": len(items),
        },
        message="Problems retrieved successfully",
    )


# ══════════════════════════════════════════════════════════════
# GET /api/problems/{id}  — full detail
# ══════════════════════════════════════════════════════════════

@router.get(
    "/{problem_id}",
    summary="Get problem details",
    description=(
        "Returns the full problem, including all visible test cases. "
        "Hidden/edge/stress test cases are excluded from this response "
        "(they are only used server-side during submission judging)."
    ),
)
async def get_problem(
    problem_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    problem = await _get_owned_problem(problem_id, current_user, db, load_test_cases=True)
    return success_response(
        data=ProblemResponse.model_validate(problem).model_dump(),
        message="Problem retrieved successfully",
    )


# ══════════════════════════════════════════════════════════════
# PUT /api/problems/{id}  — edit
# ══════════════════════════════════════════════════════════════

@router.put(
    "/{problem_id}",
    summary="Edit a problem",
    description=(
        "Update any field of a problem. Every field is optional — only send "
        "what changed. Useful for correcting AI reconstruction mistakes."
    ),
)
async def update_problem(
    problem_id: uuid.UUID,
    data: ProblemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    problem = await _get_owned_problem(problem_id, current_user, db, load_test_cases=True)

    # Apply only the fields that were explicitly sent (exclude_unset=True)
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise BadRequestException("No fields provided to update.")

    # Serialise ProblemExample objects to plain dicts if present
    if "examples" in updates and updates["examples"] is not None:
        updates["examples"] = [
            ex if isinstance(ex, dict) else ex.model_dump()
            for ex in updates["examples"]
        ]

    for field, value in updates.items():
        setattr(problem, field, value)

    await db.commit()
    await db.refresh(problem)

    result = await db.execute(
        select(Problem)
        .where(Problem.id == problem.id)
        .options(selectinload(Problem.test_cases))
    )
    problem = result.scalar_one()

    return success_response(
        data=ProblemResponse.model_validate(problem).model_dump(),
        message="Problem updated successfully",
    )


# ══════════════════════════════════════════════════════════════
# DELETE /api/problems/{id}
# ══════════════════════════════════════════════════════════════

@router.delete(
    "/{problem_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a problem",
    description=(
        "Permanently deletes the problem and all associated test cases and submissions "
        "(cascaded by the database ON DELETE CASCADE constraint)."
    ),
)
async def delete_problem(
    problem_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    problem = await _get_owned_problem(problem_id, current_user, db)
    await db.delete(problem)
    await db.commit()
    return success_response(message="Problem deleted successfully")


# ══════════════════════════════════════════════════════════════
# POST /api/problems/{id}/generate-tests  — AI test case generation
# ══════════════════════════════════════════════════════════════

@router.post(
    "/{problem_id}/generate-tests",
    status_code=status.HTTP_201_CREATED,
    summary="AI-generate test cases",
    description=(
        "Calls Google Gemini to generate diverse test cases for this problem. "
        "Generated cases are persisted and returned. "
        "Expect 5-15 seconds for this endpoint. "
        "Requires the problem to have been reconstructed (has a description)."
    ),
)
async def generate_tests(
    problem_id: uuid.UUID,
    data: GenerateTestsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Test case generation flow:
      1. Load the Problem (must be owned, must have a description)
      2. Call Gemini with the full problem context → list of test case dicts
      3. Insert all generated test cases into the DB
      4. Return the saved TestCaseResponse objects
    """
    problem = await _get_owned_problem(problem_id, current_user, db)

    generated = await generate_test_cases(
        problem=problem,
        count=data.count,
        categories=data.categories,
    )

    if not generated:
        raise BadRequestException(
            "Gemini did not return any test cases. "
            "Ensure the problem has a complete description and try again."
        )

    new_cases = [
        TestCase(
            problem_id=problem.id,
            input=tc["input"],
            expected_output=tc["expected_output"],
            category=tc["category"],
            is_visible=tc["is_visible"],
        )
        for tc in generated
    ]

    db.add_all(new_cases)
    await db.commit()

    # Refresh to populate server-generated fields (id, created_at)
    for tc in new_cases:
        await db.refresh(tc)

    return success_response(
        data=[TestCaseResponse.model_validate(tc).model_dump() for tc in new_cases],
        message=f"{len(new_cases)} test case(s) generated successfully",
    )


# ══════════════════════════════════════════════════════════════
# GET /api/problems/{id}/test-cases  — list test cases
# ══════════════════════════════════════════════════════════════

@router.get(
    "/{problem_id}/test-cases",
    summary="List test cases",
    description=(
        "Returns all test cases for a problem. The owner sees both visible and hidden cases. "
        "Use the `visible_only` query param to get only sample cases (the default for the editor view)."
    ),
)
async def list_test_cases(
    problem_id: uuid.UUID,
    visible_only: bool = Query(
        default=False,
        description="If true, only returns test cases with is_visible=true",
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Ownership check
    await _get_owned_problem(problem_id, current_user, db)

    query = select(TestCase).where(TestCase.problem_id == problem_id)
    if visible_only:
        query = query.where(TestCase.is_visible == True)  # noqa: E712
    query = query.order_by(TestCase.created_at)

    result = await db.execute(query)
    test_cases = result.scalars().all()

    return success_response(
        data=[TestCaseResponse.model_validate(tc).model_dump() for tc in test_cases],
        message="Test cases retrieved successfully",
    )


# ══════════════════════════════════════════════════════════════
# POST /api/problems/{id}/test-cases  — add manual test case
# ══════════════════════════════════════════════════════════════

@router.post(
    "/{problem_id}/test-cases",
    status_code=status.HTTP_201_CREATED,
    summary="Add a manual test case",
    description="Add a custom test case to a problem. Useful for adding edge cases you know about.",
)
async def add_test_case(
    problem_id: uuid.UUID,
    data: TestCaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_owned_problem(problem_id, current_user, db)

    tc = TestCase(
        problem_id=problem_id,
        input=data.input,
        expected_output=data.expected_output,
        category=data.category,
        is_visible=data.is_visible,
    )
    db.add(tc)
    await db.commit()
    await db.refresh(tc)

    return success_response(
        data=TestCaseResponse.model_validate(tc).model_dump(),
        message="Test case added successfully",
    )


# ══════════════════════════════════════════════════════════════
# DELETE /api/problems/{id}/test-cases/{tc_id}
# ══════════════════════════════════════════════════════════════

@router.delete(
    "/{problem_id}/test-cases/{tc_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a test case",
    description="Permanently delete a single test case from a problem.",
)
async def delete_test_case(
    problem_id: uuid.UUID,
    tc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Ownership enforced via the problem check
    await _get_owned_problem(problem_id, current_user, db)

    result = await db.execute(
        select(TestCase).where(
            TestCase.id == tc_id,
            TestCase.problem_id == problem_id,
        )
    )
    tc = result.scalar_one_or_none()
    if not tc:
        raise NotFoundException("Test case")

    await db.delete(tc)
    await db.commit()
    return success_response(message="Test case deleted successfully")
