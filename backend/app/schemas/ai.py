from typing import List, Optional

from pydantic import BaseModel, Field


# ── Feedback ────────────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    problem_id: str
    language: str
    code: str
    verdict: str
    failing_input: Optional[str] = None
    failing_expected: Optional[str] = None
    failing_actual: Optional[str] = None


class FeedbackResponse(BaseModel):
    analysis: str
    likely_bug: str
    suggested_approach: str
    code_snippet_hint: Optional[str] = None


# ── Hints ───────────────────────────────────────────────────────

class HintRequest(BaseModel):
    problem_id: str
    language: str
    code: str
    hint_level: int = Field(default=1, ge=1, le=3)


class HintResponse(BaseModel):
    hint_level: int
    hint: str
    can_go_deeper: bool


# ── Edge Cases ──────────────────────────────────────────────────

class EdgeCasesRequest(BaseModel):
    problem_id: str


class EdgeCaseItem(BaseModel):
    description: str
    example_input: Optional[str] = None
    why_tricky: str


class EdgeCasesResponse(BaseModel):
    edge_cases: List[EdgeCaseItem]
