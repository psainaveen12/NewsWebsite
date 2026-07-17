"""Initial news, comments, assets and import schema."""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "import_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("stage", sa.String(255), nullable=False),
        sa.Column("posts_created", sa.Integer(), nullable=False),
        sa.Column("posts_updated", sa.Integer(), nullable=False),
        sa.Column("pages_created", sa.Integer(), nullable=False),
        sa.Column("comments_created", sa.Integer(), nullable=False),
        sa.Column("assets_created", sa.Integer(), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=False),
        sa.Column("error", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_import_jobs_status", "import_jobs", ["status"])
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(512), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("content_html", sa.Text(), nullable=False),
        sa.Column("author_name", sa.String(255), nullable=False),
        sa.Column("original_url", sa.Text()),
        sa.Column("featured_image", sa.Text()),
        sa.Column("labels", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("view_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_articles_slug"),
        sa.UniqueConstraint("source_id", name="uq_articles_source_id"),
    )
    op.create_index("ix_articles_is_published", "articles", ["is_published"])
    op.create_index("ix_articles_publication", "articles", ["kind", "is_published", "published_at"])
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(512), nullable=False),
        sa.Column("author_name", sa.String(255), nullable=False),
        sa.Column("author_url", sa.Text()),
        sa.Column("avatar_url", sa.Text()),
        sa.Column("content_html", sa.Text(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", name="uq_comments_source_id"),
    )
    op.create_index("ix_comments_article_id", "comments", ["article_id"])
    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer()),
        sa.Column("original_name", sa.Text(), nullable=False),
        sa.Column("original_path", sa.Text(), nullable=False),
        sa.Column("public_path", sa.Text(), nullable=False),
        sa.Column("media_type", sa.String(120), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("checksum", name="uq_assets_checksum"),
    )
    op.create_index("ix_assets_article_id", "assets", ["article_id"])


def downgrade() -> None:
    op.drop_table("assets")
    op.drop_table("comments")
    op.drop_table("articles")
    op.drop_table("import_jobs")
