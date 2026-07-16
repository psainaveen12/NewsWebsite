from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.metadata import ArticleMetadata
from app.models import Article


@dataclass(slots=True)
class SaveResult:
    article: Article
    action: str


def _slug_base(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    return (slug[:180].rstrip("-") or "article")


def _unique_slug(session: Session, title: str, identity_url: str) -> str:
    base = _slug_base(title)
    existing = session.scalar(select(Article.id).where(Article.slug == base))
    if existing is None:
        return base

    suffix = hashlib.sha256(identity_url.encode("utf-8")).hexdigest()[:8]
    candidate = f"{base[:170].rstrip('-')}-{suffix}"
    counter = 2
    while session.scalar(select(Article.id).where(Article.slug == candidate)) is not None:
        candidate = f"{base[:165].rstrip('-')}-{suffix}-{counter}"
        counter += 1
    return candidate


def save_article_metadata(session: Session, metadata: ArticleMetadata) -> SaveResult:
    clauses = [Article.source_url == metadata.source_url]
    if metadata.canonical_url:
        clauses.append(Article.canonical_url == metadata.canonical_url)
    article = session.scalar(select(Article).where(or_(*clauses)))
    now = datetime.now(timezone.utc)

    if article:
        article.canonical_url = metadata.canonical_url
        article.title = metadata.title
        article.description = metadata.description
        article.image_url = metadata.image_url
        article.author = metadata.author
        article.source_name = metadata.source_name
        article.source_domain = metadata.source_domain
        article.published_at = metadata.published_at
        article.fetched_at = now
        article.updated_at = now
        article.raw_metadata = metadata.raw_metadata
        action = "updated"
    else:
        article = Article(
            source_url=metadata.source_url,
            canonical_url=metadata.canonical_url,
            slug=_unique_slug(session, metadata.title, metadata.canonical_url),
            title=metadata.title,
            description=metadata.description,
            image_url=metadata.image_url,
            author=metadata.author,
            source_name=metadata.source_name,
            source_domain=metadata.source_domain,
            published_at=metadata.published_at,
            fetched_at=now,
            raw_metadata=metadata.raw_metadata,
            is_published=True,
        )
        session.add(article)
        action = "created"

    session.flush()
    return SaveResult(article=article, action=action)


def public_articles(
    session: Session,
    query: str,
    page: int,
    page_size: int,
) -> tuple[list[Article], int]:
    filters = [Article.is_published.is_(True)]
    if query:
        filters.append(
            or_(
                Article.title.icontains(query, autoescape=True),
                Article.description.icontains(query, autoescape=True),
                Article.source_name.icontains(query, autoescape=True),
            )
        )

    total = session.scalar(select(func.count(Article.id)).where(*filters)) or 0
    articles = list(
        session.scalars(
            select(Article)
            .where(*filters)
            .order_by(Article.published_at.desc(), Article.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    return articles, total
