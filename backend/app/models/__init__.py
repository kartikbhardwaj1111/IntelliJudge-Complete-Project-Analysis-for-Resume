"""
IntelliJudge — Models Package

Import all models here so Alembic can discover them for auto-migrations,
and so SQLAlchemy can resolve relationship references between models.

ORDER MATTERS: import Base first, then models in dependency order
(User before Problem/Submission, Problem before TestCase/Submission).
"""

from app.database import Base  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.problem import Problem  # noqa: F401
from app.models.test_case import TestCase  # noqa: F401
from app.models.submission import Submission  # noqa: F401

__all__ = ["Base", "User", "Problem", "TestCase", "Submission"]
