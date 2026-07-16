from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.metadata import ArticleMetadata, MetadataFetchError, ensure_public_url, normalize_http_url


def make_settings(tmp_path) -> Settings:
    return Settings(
        environment="testing",
        app_name="Test Newsroom",
        allowed_hosts="testserver,localhost,127.0.0.1",
        cookie_secure=False,
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        admin_username="sainaveennews",
        admin_password="correct-test-password",
        session_secret="test-session-secret-that-is-long-enough",
        page_size=12,
    )


def csrf_from(response) -> str:
    match = re.search(r'name="csrf" value="([^"]+)"', response.text)
    assert match
    return match.group(1)


def login(client: TestClient, password: str = "correct-test-password"):
    login_page = client.get("/login")
    return client.post(
        "/login",
        data={
            "username": "sainaveennews",
            "password": password,
            "csrf": csrf_from(login_page),
        },
        follow_redirects=False,
    )


def test_public_home_and_health(tmp_path):
    app = create_app(make_settings(tmp_path))
    with TestClient(app) as client:
        home = client.get("/")
        assert home.status_code == 200
        assert "The first edition is being prepared" in home.text
        health = client.get("/healthz")
        assert health.status_code == 200
        assert health.json() == {"status": "ok", "database": "ok"}


def test_admin_requires_login_and_rejects_bad_password(tmp_path):
    app = create_app(make_settings(tmp_path))
    with TestClient(app) as client:
        protected = client.get("/admin", follow_redirects=False)
        assert protected.status_code == 303
        assert protected.headers["location"] == "/login"

        failed = login(client, "wrong-password")
        assert failed.status_code == 401
        assert "Invalid username or password" in failed.text

        authenticated = login(client)
        assert authenticated.status_code == 303
        assert authenticated.headers["location"] == "/admin"
        assert client.get("/admin").status_code == 200


def test_bulk_import_deduplicates_and_displays_articles(tmp_path):
    app = create_app(make_settings(tmp_path))

    async def fake_fetch(url: str, settings: Settings) -> ArticleMetadata:
        number = url.rsplit("-", 1)[-1]
        return ArticleMetadata(
            source_url=url,
            canonical_url=url,
            title=f"Imported Article {number}",
            description=f"Description for article {number}",
            image_url="https://images.example.com/article.jpg",
            author="News Author",
            source_name="Example Publisher",
            source_domain="example.com",
            published_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
            raw_metadata={"og_type": "article"},
        )

    app.state.metadata_fetcher = fake_fetch
    with TestClient(app) as client:
        assert login(client).status_code == 303
        admin = client.get("/admin")
        imported = client.post(
            "/admin/articles/import",
            data={
                "urls": "https://example.com/article-1\nhttps://example.com/article-2",
                "csrf": csrf_from(admin),
            },
        )
        assert imported.status_code == 200
        assert "Created: Imported Article 1" in imported.text
        assert "Created: Imported Article 2" in imported.text

        home = client.get("/")
        assert "Imported Article 1" in home.text
        assert "Imported Article 2" in home.text
        assert "2 stories" in home.text

        admin = client.get("/admin")
        updated = client.post(
            "/admin/articles/import",
            data={"urls": "https://example.com/article-1", "csrf": csrf_from(admin)},
        )
        assert "Updated: Imported Article 1" in updated.text
        assert "2 stories" in client.get("/").text
        detail = client.get("/articles/imported-article-1")
        assert detail.status_code == 200
        assert "Description for article 1" in detail.text


def test_url_validation_blocks_unsafe_targets():
    with pytest.raises(MetadataFetchError):
        normalize_http_url("file:///etc/passwd")
    with pytest.raises(MetadataFetchError):
        normalize_http_url("http://user:pass@example.com/article")
    with pytest.raises(MetadataFetchError):
        asyncio.run(ensure_public_url("http://127.0.0.1/private"))
