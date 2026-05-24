"""
Alembic Migration Environment

This file runs every time you use an alembic command.
It connects to the database and applies/generates migrations.

KEY THINGS THIS FILE DOES:
  1. Imports our Base model (which knows about all our tables)
  2. Gets the DATABASE_URL from our settings (not from alembic.ini)
  3. Configures the migration engine to work in async mode
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import settings

# Import ALL models so Alembic can detect them for auto-migrations
# This import triggers app/models/__init__.py which imports User, etc.
from app.models import Base  # noqa: F401

# Alembic Config object — provides access to alembic.ini values
config = context.config

# Set the database URL from our settings (overrides alembic.ini placeholder)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is the MetaData object that contains all our table definitions
# Alembic compares this against the actual database to generate migrations
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    Generates SQL scripts without connecting to the database.
    Useful for reviewing what SQL will be executed.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Helper to run migrations with a given connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in 'online' mode with async engine.
    
    Creates a real connection to the database and applies migrations.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online migrations — runs the async version."""
    asyncio.run(run_async_migrations())


# Decide which mode to run in
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
