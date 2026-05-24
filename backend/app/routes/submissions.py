"""
IntelliJudge — Submission Routes

All endpoints require a valid JWT (Bearer token).
Users can only run/submit against problems they own.

Endpoints:
  POST /api/submissions/run       Execute code with custom stdin (no DB record)
  POST /api/submissions/submit    Judge code against all test cases (stores in DB)
  GET  /api/submissions/{id}      Retrieve a past submission

DESIGN DECISIONS:
  - /run  → fire-and-forget execution, useful for "Run" button before submitting
  - /submit → sequential Judge0 calls per test case to respect rate limits;
             early exit on CE (remaining cases would also CE)
  - Rate-limit guard: 300 ms sleep between test case executions on free tier
  - CE from Judge0 is detected via status_id 6 — compile_output has the error
"""

import asyncio
import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.test_case import TestCase
from app.models.user import User
from app.schemas.submission import (
    RunRequest,
    RunResponse,
    SubmissionResponse,
    SubmitRequest,
)
from app.services.compiler_service import run_code
from app.services.validation_service import build_test_case_result, compute_verdict
from app.utils.exceptions import BadRequestException, NotFoundException, success_response
from app.utils.jwt import get_current_user

router = APIRouter()


# ── Ownership helper ──────────────────────────────────────────────────────────

async def _get_owned_problem(
    problem_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> Problem:
    result = await db.execute(
        select(Problem).where(
            Problem.id == problem_id,
            Problem.user_id == current_user.id,
        )
    )
    problem = result.scalar_one_or_none()
    if not problem:
        raise NotFoundException("Problem")
    return problem


# ── POST /run ─────────────────────────────────────────────────────────────────

@router.post(
    "/run",
    status_code=status.HTTP_200_OK,
    summary="Run code with custom input",
    description=(
        "Execute source code in the selected language with a custom stdin. "
        "No submission record is created — use this for the 'Run' button "
        "so users can test their code interactively before submitting."
    ),
)
async def run(
    data: RunRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Single execution flow:
      1. Ownership check (problem must belong to current user)
      2. Submit to Judge0 with base64-encoded source_code + stdin
      3. Return normalised result (verdict, stdout, stderr, runtime, memory)

    No DB write — the result is transient.
    """
    await _get_owned_problem(data.problem_id, current_user, db)

    try:
        result = await run_code(
            language=data.language,
            code=data.code,
            stdin=data.stdin,
        )
    except ValueError as exc:
        raise BadRequestException(str(exc))
    except RuntimeError as exc:
        raise BadRequestException(str(exc))
    except Exception:
        raise BadRequestException(
            "Code execution service is unavailable. "
            "Make sure g++/python3/node/javac are installed and try again."
        )

    return success_response(
        data=RunResponse(**result).model_dump(),
        message="Code executed",
    )


# ── POST /submit ──────────────────────────────────────────────────────────────

@router.post(
    "/submit",
    status_code=status.HTTP_201_CREATED,
    summary="Submit code for judging",
    description=(
        "Run source code against ALL test cases for the problem. "
        "Stores the submission (verdict + per-case results) in the database. "
        "Returns the final verdict and per-test-case breakdown. "
        "Expect 5–30 seconds depending on the number of test cases."
    ),
)
async def submit(
    data: SubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Full submission judging flow:
      1. Ownership check
      2. Load all test cases for this problem
      3. For each test case:
         a. Submit code to Judge0 with tc.input as stdin
         b. Build a per-case result dict (verdict, runtime, memory, output diff)
         c. Early exit on CE — remaining cases would also fail to compile
         d. Sleep 300 ms between calls (free-tier rate limit guard)
      4. Compute overall verdict (worst-of-all)
      5. Insert Submission record → DB
      6. Return SubmissionResponse
    """
    await _get_owned_problem(data.problem_id, current_user, db)

    # Load test cases
    tc_result = await db.execute(
        select(TestCase)
        .where(TestCase.problem_id == data.problem_id)
        .order_by(TestCase.created_at)
    )
    test_cases: List[TestCase] = list(tc_result.scalars().all())

    if not test_cases:
        raise BadRequestException(
            "This problem has no test cases. "
            "Generate test cases first (POST /api/problems/{id}/generate-tests)."
        )

    # Run each test case against Judge0
    case_results = []
    for tc in test_cases:
        try:
            judge_result = await run_code(
                language=data.language,
                code=data.code,
                stdin=tc.input,
            )
        except Exception:
            # Network / API error — treat this test case as RE
            judge_result = {
                "verdict": "RE",
                "stdout": None,
                "stderr": "Execution service error during judging.",
                "compile_output": None,
                "runtime_ms": None,
                "memory_kb": None,
                "status_description": "Service Error",
            }

        case_result = build_test_case_result(
            test_case_id=str(tc.id),
            judge_result=judge_result,
            expected_output=tc.expected_output,
            input_text=tc.input,
            is_visible=tc.is_visible,
        )
        case_results.append(case_result)

        # CE means compilation failed — remaining cases will also fail
        if case_result["verdict"] == "CE":
            break

        # 300 ms guard to stay within Judge0 free-tier rate limits
        if len(test_cases) > 1:
            await asyncio.sleep(0.3)

    # Compute overall verdict and summary stats
    overall_verdict = compute_verdict(case_results)
    passed = sum(1 for r in case_results if r["verdict"] == "AC")

    runtimes = [r["runtime_ms"] for r in case_results if r.get("runtime_ms") is not None]
    memories = [r["memory_kb"] for r in case_results if r.get("memory_kb") is not None]

    # Persist submission
    submission = Submission(
        user_id=current_user.id,
        problem_id=data.problem_id,
        language=data.language,
        code=data.code,
        verdict=overall_verdict,
        runtime_ms=round(max(runtimes)) if runtimes else None,
        memory_kb=max(memories) if memories else None,
        test_cases_passed=passed,
        total_test_cases=len(test_cases),
        results=case_results,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    return success_response(
        data=SubmissionResponse.model_validate(submission).model_dump(),
        message=(
            f"{overall_verdict} — {passed}/{len(test_cases)} test cases passed"
        ),
    )


# ── GET /{id} ─────────────────────────────────────────────────────────────────

@router.get(
    "/{submission_id}",
    summary="Get submission details",
    description=(
        "Retrieve the full details of a past submission, "
        "including the per-test-case results breakdown."
    ),
)
async def get_submission(
    submission_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Submission).where(
            Submission.id == submission_id,
            Submission.user_id == current_user.id,
        )
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise NotFoundException("Submission")

    return success_response(
        data=SubmissionResponse.model_validate(submission).model_dump(),
        message="Submission retrieved",
    )
