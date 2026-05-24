"""
IntelliJudge — Problem & TestCase Pydantic Schemas

INPUT schemas  → validate request bodies coming in from the client.
OUTPUT schemas → control exactly what fields get serialised in responses.
                 Nothing here leaks internal implementation details.

Schema hierarchy:
  ProblemExample         — one input/output pair (used inside ProblemResponse)
  TestCaseResponse       — a single test case row returned to the client
  ReconstructRequest     — body for POST /api/problems/reconstruct
  ProblemCreate          — body for creating a problem manually (no OCR)
  ProblemUpdate          — body for PATCH/PUT edits after AI reconstruction
  ProblemResponse        — full problem row (with test cases list)
  ProblemListItem        — lightweight card for GET /api/problems list view
  GenerateTestsRequest   — body for POST /api/problems/{id}/generate-tests
  TestCaseCreate         — body for POST /api/problems/{id}/test-cases (manual add)
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ─── Nested / Shared ───────────────────────────────────────────


class ProblemExample(BaseModel):
    """
    One example from the problem statement.
    Stored as JSONB in the problems.examples column.
    """

    input: str
    output: str
    explanation: Optional[str] = None


# ─── TestCase Schemas ──────────────────────────────────────────


class TestCaseResponse(BaseModel):
    """Returned for every test case that is visible to the user."""

    id: uuid.UUID
    problem_id: uuid.UUID
    input: str
    expected_output: str
    category: str          # "sample" | "hidden" | "edge" | "stress"
    is_visible: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TestCaseCreate(BaseModel):
    """
    Body for POST /api/problems/{id}/test-cases.
    Allows users to add a custom test case manually.
    """

    input: str = Field(..., min_length=1, description="Test case input")
    expected_output: str = Field(..., min_length=1, description="Expected output for this input")
    category: str = Field(
        default="sample",
        pattern=r"^(sample|hidden|edge|stress)$",
        description="One of: sample, hidden, edge, stress",
    )
    is_visible: bool = Field(
        default=True,
        description="Whether this test case is shown to the user",
    )


# ─── Problem Request Schemas ───────────────────────────────────


class ReconstructRequest(BaseModel):
    """
    Body for POST /api/problems/reconstruct.

    The client sends the problem_id returned by POST /api/upload/screenshot.
    Optionally, ocr_text can be overridden (e.g. if the user corrected the OCR output).
    """

    problem_id: uuid.UUID = Field(..., description="ID of the partial Problem created by the upload step")
    ocr_text_override: Optional[str] = Field(
        default=None,
        description="If provided, this text is sent to Gemini instead of the stored OCR text. "
                    "Useful when the user has manually corrected OCR errors.",
    )


class ProblemCreate(BaseModel):
    """
    Body for creating a problem without OCR (typed manually).
    All required fields must be provided up front.
    """

    title: str = Field(..., min_length=3, max_length=500)
    description: str = Field(..., min_length=10)
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None
    examples: Optional[List[ProblemExample]] = None
    difficulty: Optional[str] = Field(
        default=None,
        pattern=r"^(easy|medium|hard)$",
        description="One of: easy, medium, hard",
    )
    tags: Optional[List[str]] = None


class ProblemUpdate(BaseModel):
    """
    Body for PUT /api/problems/{id}.

    Every field is optional so the client can send only what changed.
    The AI reconstruction result can be corrected field-by-field.
    """

    title: Optional[str] = Field(default=None, min_length=3, max_length=500)
    description: Optional[str] = Field(default=None, min_length=10)
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None
    examples: Optional[List[ProblemExample]] = None
    difficulty: Optional[str] = Field(
        default=None,
        pattern=r"^(easy|medium|hard)$",
    )
    tags: Optional[List[str]] = None


class GenerateTestsRequest(BaseModel):
    """
    Body for POST /api/problems/{id}/generate-tests.

    count — how many test cases to ask Gemini to generate (1-20).
    categories — which categories to generate. Defaults to all three.
    """

    count: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of test cases to generate (1-20)",
    )
    categories: List[str] = Field(
        default=["sample", "edge", "hidden"],
        description="Categories to generate. Each must be one of: sample, edge, hidden, stress",
    )


# ─── Problem Response Schemas ──────────────────────────────────


class ProblemResponse(BaseModel):
    """
    Full problem detail — returned by GET /api/problems/{id}
    and POST /api/problems/reconstruct.

    test_cases only includes is_visible=True cases by default.
    Hidden/edge/stress cases are never returned here (they are used
    only server-side during submission judging).
    """

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str
    input_format: Optional[str]
    output_format: Optional[str]
    constraints: Optional[Dict[str, Any]]
    examples: Optional[List[Dict[str, Any]]]
    difficulty: Optional[str]
    tags: Optional[List[str]]
    ocr_text: Optional[str]
    screenshot_url: Optional[str]
    created_at: datetime
    test_cases: List[TestCaseResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ProblemListItem(BaseModel):
    """
    Lightweight card for GET /api/problems (dashboard list view).
    Excludes heavy text fields (description, ocr_text) to keep the payload small.
    """

    id: uuid.UUID
    title: str
    difficulty: Optional[str]
    tags: Optional[List[str]]
    screenshot_url: Optional[str]
    created_at: datetime
    test_case_count: int = 0

    model_config = ConfigDict(from_attributes=True)
