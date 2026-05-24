"""
IntelliJudge — Submission Pydantic Schemas

INPUT schemas  → validate request bodies from the frontend editor.
OUTPUT schemas → control exactly what fields are serialised in responses.

RunRequest     — POST /api/submissions/run   (custom input, no DB record)
SubmitRequest  — POST /api/submissions/submit (judge all test cases, store in DB)
RunResponse    — result of a single execution (not persisted)
SubmissionResponse — full submission row returned to the client
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Requests ──────────────────────────────────────────────────────────────────


class RunRequest(BaseModel):
    """
    Body for POST /api/submissions/run.
    Executes code with the user's custom stdin — no submission record created.
    """

    problem_id: uuid.UUID = Field(
        ..., description="ID of the problem being solved"
    )
    language: str = Field(
        ...,
        pattern=r"^(cpp|java|python|javascript)$",
        description="Language key: cpp | java | python | javascript",
    )
    code: str = Field(..., min_length=1, description="Full source code")
    stdin: str = Field(
        default="",
        description="Custom stdin to pass to the program",
    )


class SubmitRequest(BaseModel):
    """
    Body for POST /api/submissions/submit.
    Runs code against all test cases for the problem and stores the verdict in DB.
    """

    problem_id: uuid.UUID = Field(
        ..., description="ID of the problem being submitted"
    )
    language: str = Field(
        ...,
        pattern=r"^(cpp|java|python|javascript)$",
        description="Language key: cpp | java | python | javascript",
    )
    code: str = Field(..., min_length=1, description="Full source code")


# ── Responses ─────────────────────────────────────────────────────────────────


class RunResponse(BaseModel):
    """
    Result of a single code execution (POST /api/submissions/run).
    Not persisted — just returned to the client.
    """

    verdict: str = Field(
        ..., description="AC | CE | RE | TLE — does NOT check expected output"
    )
    stdout: Optional[str] = Field(None, description="Program standard output")
    stderr: Optional[str] = Field(None, description="Program standard error")
    compile_output: Optional[str] = Field(
        None, description="Compiler output (set when verdict is CE)"
    )
    runtime_ms: Optional[float] = Field(
        None, description="Execution time in milliseconds"
    )
    memory_kb: Optional[int] = Field(
        None, description="Peak memory usage in KB"
    )
    status_description: str = Field(
        ..., description="Human-readable status from Judge0"
    )


class SubmissionResponse(BaseModel):
    """
    Full submission record — returned after POST /api/submissions/submit
    and GET /api/submissions/{id}.

    The `results` field is the per-test-case breakdown (see Submission model
    docstring for the shape of each element).
    """

    id: uuid.UUID
    problem_id: uuid.UUID
    language: str
    verdict: str = Field(
        ...,
        description="Overall verdict: AC | WA | TLE | MLE | RE | CE | pending",
    )
    runtime_ms: Optional[int] = Field(
        None, description="Max runtime across all test cases (ms)"
    )
    memory_kb: Optional[int] = Field(
        None, description="Max memory across all test cases (KB)"
    )
    test_cases_passed: int
    total_test_cases: int
    results: Optional[List[Dict[str, Any]]] = Field(
        None,
        description=(
            "Per-test-case results. Each element has: "
            "test_case_id, verdict, runtime_ms, memory_kb, "
            "actual_output, expected_output, input, is_visible."
        ),
    )
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
