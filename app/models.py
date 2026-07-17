import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ImportJob(Base):
    __tablename__ = "import_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(24), default="queued", index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    stage: Mapped[str] = mapped_column(String(255), default="Queued")
    posts_created: Mapped[int] = mapped_column(Integer, default=0)
    posts_updated: Mapped[int] = mapped_column(Integer, default=0)
    pages_created: Mapped[int] = mapped_column(Integer, default=0)
    comments_created: Mapped[int] = mapped_column(Integer, default=0)
    assets_created: Mapped[int] = mapped_column(Integer, default=0)
    warnings: Mapped[list] = mapped_column(JSON, default=list)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (
        UniqueConstraint("source_id", name="uq_articles_source_id"),
        UniqueConstraint("slug", name="uq_articles_slug"),
        Index("ix_articles_publication", "kind", "is_published", "published_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[str] = mapped_column(String(512))
    kind: Mapped[str] = mapped_column(String(16), default="post")
    slug: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str] = mapped_column(Text, default="")
    content_html: Mapped[str] = mapped_column(Text, default="")
    author_name: Mapped[str] = mapped_column(String(255), default="Editorial Desk")
    original_url: Mapped[str | None] = mapped_column(Text)
    featured_image: Mapped[str | None] = mapped_column(Text)
    labels: Mapped[list] = mapped_column(JSON, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[list["Comment"]] = relationship(back_populates="article", cascade="all, delete-orphan")
    assets: Mapped[list["Asset"]] = relationship(back_populates="article", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (UniqueConstraint("source_id", name="uq_comments_source_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    source_id: Mapped[str] = mapped_column(String(512))
    author_name: Mapped[str] = mapped_column(String(255), default="Anonymous")
    author_url: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    content_html: Mapped[str] = mapped_column(Text, default="")
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    article: Mapped[Article] = relationship(back_populates="comments")


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = (UniqueConstraint("checksum", name="uq_assets_checksum"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int | None] = mapped_column(ForeignKey("articles.id", ondelete="SET NULL"), index=True)
    original_name: Mapped[str] = mapped_column(Text)
    original_path: Mapped[str] = mapped_column(Text)
    public_path: Mapped[str] = mapped_column(Text)
    media_type: Mapped[str] = mapped_column(String(120))
    checksum: Mapped[str] = mapped_column(String(64))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    article: Mapped[Article | None] = relationship(back_populates="assets")
