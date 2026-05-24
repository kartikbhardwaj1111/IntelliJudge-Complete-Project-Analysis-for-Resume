"""create problems, test_cases, and submissions tables

Revision ID: 2026_05_09_0002
Revises: 2026_05_09_0001
Create Date: 2026-05-09 00:01:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2026_05_09_0002"
down_revision: Union[str, Sequence[str], None] = "2026_05_09_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── problems ────────────────────────────────────────────────
    op.create_table(
        "problems",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("input_format", sa.Text, nullable=True),
        sa.Column("output_format", sa.Text, nullable=True),
        sa.Column(
            "constraints",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "examples",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("difficulty", sa.String(length=20), nullable=True),
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("ocr_text", sa.Text, nullable=True),
        sa.Column("screenshot_url", sa.String(length=1000), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )
    op.create_index(op.f("ix_problems_user_id"), "problems", ["user_id"], unique=False)
    op.create_index(op.f("ix_problems_difficulty"), "problems", ["difficulty"], unique=False)

    # ── test_cases ──────────────────────────────────────────────
    op.create_table(
        "test_cases",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "problem_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("problems.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("input", sa.Text, nullable=False),
        sa.Column("expected_output", sa.Text, nullable=False),
        sa.Column(
            "category",
            sa.String(length=20),
            nullable=False,
            server_default="sample",
        ),
        sa.Column(
            "is_visible",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )
    op.create_index(
        op.f("ix_test_cases_problem_id"), "test_cases", ["problem_id"], unique=False
    )

    # ── submissions ─────────────────────────────────────────────
    op.create_table(
        "submissions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "problem_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("problems.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("code", sa.Text, nullable=False),
        sa.Column(
            "verdict",
            sa.String(length=20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("runtime_ms", sa.Integer, nullable=True),
        sa.Column("memory_kb", sa.Integer, nullable=True),
        sa.Column(
            "test_cases_passed",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "total_test_cases",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "results",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )
    op.create_index(
        op.f("ix_submissions_user_id"), "submissions", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_submissions_problem_id"), "submissions", ["problem_id"], unique=False
    )
    op.create_index(
        op.f("ix_submissions_verdict"), "submissions", ["verdict"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_submissions_verdict"), table_name="submissions")
    op.drop_index(op.f("ix_submissions_problem_id"), table_name="submissions")
    op.drop_index(op.f("ix_submissions_user_id"), table_name="submissions")
    op.drop_table("submissions")

    op.drop_index(op.f("ix_test_cases_problem_id"), table_name="test_cases")
    op.drop_table("test_cases")

    op.drop_index(op.f("ix_problems_difficulty"), table_name="problems")
    op.drop_index(op.f("ix_problems_user_id"), table_name="problems")
    op.drop_table("problems")
