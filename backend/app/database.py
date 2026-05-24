"""
IntelliJudge — Database Connection

Sets up the async connection to PostgreSQL using SQLAlchemy.

KEY CONCEPTS:
  1. Engine — the connection pool to the database
  2. SessionLocal — a factory that creates database sessions
  3. get_db() — a dependency that gives routes a session and auto-closes it

WHY ASYNC?
  - FastAPI is async, so we use async SQLAlchemy to avoid blocking
  - asyncpg is the fastest PostgreSQL driver for Python
  - This means our API can handle many concurrent requests efficiently

USAGE IN ROUTES:
  @router.get("/users")
  async def get_users(db: AsyncSession = Depends(get_db)):
      result = await db.execute(select(User))
      return result.scalars().all()
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# ─── Database Engine ───────────────────────────────────────────
# The engine manages the connection pool to PostgreSQL.
# - pool_size: how many connections to keep open (5 is fine for dev)
# - echo: if True, prints all SQL queries to console (great for learning!)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Print SQL queries in debug mode
    pool_size=5,
    max_overflow=10,
)


# ─── Session Factory ──────────────────────────────────────────
# A session = one "conversation" with the database.
# Each API request gets its own session, which is closed after the request.

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit (avoids lazy load issues)
)


# ─── Base Model Class ─────────────────────────────────────────
# All our database models (User, Problem, etc.) will inherit from this.
# SQLAlchemy uses this to track all models and generate migrations.

class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# ─── Dependency: Get Database Session ─────────────────────────
# This is a FastAPI "dependency" — routes can request a DB session
# by adding `db: AsyncSession = Depends(get_db)` to their parameters.
#
# The `yield` pattern ensures the session is ALWAYS closed,
# even if an error occurs during the request.

async def get_db():
    """
    Provides a database session for a single request.
    
    Usage:
        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            # use db here
            pass
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
