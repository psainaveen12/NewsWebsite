import json
import re

from sqlalchemy import func, select

from app.config import get_settings
from app.database import SessionLocal
from app.models import Article, Asset, Comment


MEDIA_REFERENCE_PATTERN = re.compile(r'(?:src|href)=["\'](/media/[^"\']+)')


def build_migration_report() -> dict:
    settings = get_settings()
    with SessionLocal() as session:
        articles = list(session.scalars(select(Article)))
        media_paths = set(MEDIA_REFERENCE_PATTERN.findall("\n".join(item.content_html for item in articles)))
        broken_media = [
            path
            for path in sorted(media_paths)
            if not (settings.media_dir / path.removeprefix("/media/")).is_file()
        ]
        return {
            "posts": sum(item.kind == "post" for item in articles),
            "pages": sum(item.kind == "page" for item in articles),
            "published_posts": sum(item.kind == "post" and item.is_published for item in articles),
            "comments": session.scalar(select(func.count()).select_from(Comment)) or 0,
            "assets": session.scalar(select(func.count()).select_from(Asset)) or 0,
            "broken_local_media": broken_media[:100],
            "remaining_www_internal_links": sum(
                item.content_html.count("www.ieltstask.com") for item in articles
            ),
        }


if __name__ == "__main__":
    report = build_migration_report()
    print(json.dumps(report, indent=2))
    if report["broken_local_media"]:
        raise SystemExit(1)
