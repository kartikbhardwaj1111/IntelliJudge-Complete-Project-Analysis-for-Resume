from typing import List, Optional

from pydantic import BaseModel


class OverviewStats(BaseModel):
    total_problems: int
    total_submissions: int
    solved_problems: int
    acceptance_rate: float
    avg_runtime_ms: Optional[float] = None


class DifficultyBucket(BaseModel):
    total: int
    solved: int


class DifficultyStats(BaseModel):
    easy: DifficultyBucket
    medium: DifficultyBucket
    hard: DifficultyBucket
    unknown: DifficultyBucket


class TagStat(BaseModel):
    tag: str
    total: int
    solved: int
    accuracy: float


class TagStats(BaseModel):
    tags: List[TagStat]


class ActivityPoint(BaseModel):
    date: str
    submissions: int
    accepted: int


class ActivityStats(BaseModel):
    days: List[ActivityPoint]


class SubmissionHistoryItem(BaseModel):
    id: str
    problem_id: str
    problem_title: str
    language: str
    verdict: str
    test_cases_passed: int
    total_test_cases: int
    runtime_ms: Optional[int] = None
    created_at: str


class SubmissionHistory(BaseModel):
    items: List[SubmissionHistoryItem]
    total: int
    page: int
    pages: int
