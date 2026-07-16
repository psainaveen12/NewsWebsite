"""Create articles table.

Revision ID: 0001
Revises:
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_url", sa.Text(), nullable=False, unique=True),
        sa.Column("canonical_url", sa.Text(), nullable=True, unique=True),
        sa.Column("slug", sa.String(length=220), nullable=False, unique=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("author", sa.String(length=300), nullable=True),
        sa.Column("source_name", sa.String(length=300), nullable=True),
        sa.Column("source_domain", sa.String(length=253), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_published", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("raw_metadata", sa.JSON(), server_default=sa.text("'{}'::json"), nullable=False),
    )
    op.create_index("ix_articles_source_domain", "articles", ["source_domain"])
    op.create_index("ix_articles_published_at", "articles", ["published_at"])
    op.create_index(
        "ix_articles_publication",
        "articles",
        ["is_published", "published_at", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_articles_publication", table_name="articles")
    op.drop_index("ix_articles_published_at", table_name="articles")
    op.drop_index("ix_articles_source_domain", table_name="articles")
    op.drop_table("articles")
