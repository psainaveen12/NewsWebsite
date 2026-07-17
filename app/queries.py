from collections import Counter

from sqlalchemy import Text, cast, func, or_, select
from sqlalchemy.orm import Session

from app.models import Article


PAGE_SIZE = 10


def public_posts_query():
    return select(Article).where(Article.kind == "post", Article.is_published.is_(True))


def latest_posts(session: Session, limit: int = PAGE_SIZE, offset: int = 0) -> list[Article]:
    return list(
        session.scalars(public_posts_query().order_by(Article.published_at.desc()).limit(limit).offset(offset))
    )


def popular_posts(session: Session, limit: int = 5) -> list[Article]:
    return list(
        session.scalars(
            public_posts_query().order_by(Article.view_count.desc(), Article.published_at.desc()).limit(limit)
        )
    )


def count_posts(session: Session) -> int:
    return session.scalar(
        select(func.count()).select_from(Article).where(Article.kind == "post", Article.is_published.is_(True))
    ) or 0


def category_posts(session: Session, label: str, limit: int, offset: int = 0) -> list[Article]:
    marker = f'%"{label.lower()}"%'
    return list(
        session.scalars(
            public_posts_query()
            .where(func.lower(cast(Article.labels, Text)).like(marker))
            .order_by(Article.published_at.desc())
            .limit(limit)
            .offset(offset)
        )
    )


def search_posts(session: Session, query: str, limit: int, offset: int = 0) -> list[Article]:
    pattern = f"%{query}%"
    return list(
        session.scalars(
            public_posts_query()
            .where(or_(Article.title.ilike(pattern), Article.summary.ilike(pattern), Article.content_html.ilike(pattern)))
            .order_by(Article.published_at.desc())
            .limit(limit)
            .offset(offset)
        )
    )


def top_labels(session: Session, limit: int = 10) -> list[tuple[str, int]]:
    labels = session.scalars(
        select(Article.labels)
        .where(Article.kind == "post", Article.is_published.is_(True))
        .order_by(Article.published_at.desc())
        .limit(500)
    )
    counts: Counter[str] = Counter()
    canonical: dict[str, str] = {}
    for article_labels in labels:
        for label in article_labels or []:
            key = str(label).casefold()
            canonical.setdefault(key, str(label))
            counts[key] += 1
    return [(canonical[key], count) for key, count in counts.most_common(limit)]
