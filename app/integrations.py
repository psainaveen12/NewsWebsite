import json
import logging
from urllib.request import Request, urlopen

from app.config import Settings, get_settings


logger = logging.getLogger(__name__)


def submit_indexnow(urls: list[str], settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    unique_urls = list(dict.fromkeys(url for url in urls if url.startswith(settings.app_base_url)))[:10000]
    if not settings.indexnow_key or not unique_urls:
        return False

    payload = json.dumps(
        {
            "host": settings.app_domain,
            "key": settings.indexnow_key,
            "keyLocation": f"{settings.app_base_url}/{settings.indexnow_key}.txt",
            "urlList": unique_urls,
        }
    ).encode()
    request = Request(
        "https://api.indexnow.org/indexnow",
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "IELTSTask-News/1.0"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:  # noqa: S310 - fixed IndexNow endpoint.
            return response.status in {200, 202}
    except Exception as exc:
        logger.warning("IndexNow submission failed: %s", exc)
        return False


def submit_all_published() -> tuple[int, bool]:
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models import Article

    settings = get_settings()
    with SessionLocal() as session:
        articles = session.scalars(select(Article).where(Article.is_published.is_(True)))
        urls = [
            f"{settings.app_base_url}/{'p' if article.kind == 'page' else 'article'}/{article.slug}"
            for article in articles
        ]
    return len(urls), submit_indexnow(urls, settings)


if __name__ == "__main__":
    url_count, accepted = submit_all_published()
    if not get_settings().indexnow_key:
        print("IndexNow is disabled because INDEXNOW_KEY is empty.")
    elif accepted:
        print(f"IndexNow accepted {url_count} published URLs.")
    else:
        raise SystemExit(f"IndexNow did not accept the batch of {url_count} published URLs.")
