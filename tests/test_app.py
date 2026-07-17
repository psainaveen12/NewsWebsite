import io
import os
import shutil
import zipfile
from pathlib import Path

os.environ["APP_ENV"] = "test"
os.environ["APP_BASE_URL"] = "http://testserver"
os.environ["DATABASE_URL"] = "sqlite:////tmp/newswebsite-docker-test.db"
os.environ["DATA_DIR"] = "/tmp/newswebsite-docker-test-data"
os.environ["SESSION_SECRET"] = "test-session-secret-with-more-than-32-characters"
os.environ["ADMIN_USERNAME"] = "sainaveennews"
os.environ["ADMIN_PASSWORD"] = "test-admin-password-12345"
os.environ["BING_SITE_VERIFICATION"] = "test-bing-verification"
os.environ["ADSENSE_PUBLISHER_ID"] = "ca-pub-1234567890123456"

Path("/tmp/newswebsite-docker-test.db").unlink(missing_ok=True)
shutil.rmtree("/tmp/newswebsite-docker-test-data", ignore_errors=True)

from bs4 import BeautifulSoup  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import func, select  # noqa: E402

from app.audit import build_migration_report  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Article, Asset, Comment, ImportJob  # noqa: E402


Base.metadata.create_all(engine)


def takeout_zip(title: str = "A Test Story") -> bytes:
    atom = f'''<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:app="http://purl.org/atom/app#"
      xmlns:thr="http://purl.org/syndication/thread/1.0"
      xmlns:gd="http://schemas.google.com/g/2005">
      <entry>
        <id>tag:blogger.com,1999:blog-1.post-100</id>
        <published>2026-07-15T13:30:00Z</published><updated>2026-07-15T14:00:00Z</updated>
        <category scheme="http://schemas.google.com/g/2005#kind" term="http://schemas.google.com/blogger/2008/kind#post"/>
        <category scheme="http://www.blogger.com/atom/ns#" term="World News"/>
        <title>{title}</title>
        <content type="html">&lt;p&gt;Imported body with useful reporting.&lt;/p&gt;&lt;a href="https://www.ieltstask.com/p/about-us.html"&gt;About&lt;/a&gt;&lt;img src="Blogger/Media/news.jpg" alt="News image"&gt;&lt;script&gt;bad()&lt;/script&gt;</content>
        <author><name>sai</name><uri>https://example.com/author</uri></author>
        <link rel="alternate" href="https://www.ieltstask.com/2026/07/a-test-story.html"/>
      </entry>
      <entry>
        <id>tag:blogger.com,1999:blog-1.page-200</id>
        <published>2025-01-01T00:00:00Z</published><updated>2025-01-01T00:00:00Z</updated>
        <category scheme="http://schemas.google.com/g/2005#kind" term="http://schemas.google.com/blogger/2008/kind#page"/>
        <title>About Us</title><content type="html">&lt;p&gt;About the newsroom.&lt;/p&gt;</content>
        <author><name>sai</name></author><link rel="alternate" href="https://www.ieltstask.com/p/about-us.html"/>
      </entry>
      <entry>
        <id>tag:blogger.com,1999:blog-1.comment-300</id>
        <published>2026-07-15T15:00:00Z</published><updated>2026-07-15T15:00:00Z</updated>
        <category scheme="http://schemas.google.com/g/2005#kind" term="http://schemas.google.com/blogger/2008/kind#comment"/>
        <title>Comment</title><content type="html">&lt;p&gt;Insightful comment.&lt;/p&gt;</content>
        <author><name>Reader</name></author>
        <thr:in-reply-to ref="tag:blogger.com,1999:blog-1.post-100" href="https://www.ieltstask.com/2026/07/a-test-story.html"/>
      </entry>
    </feed>'''
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("Takeout/Blogger/Blogs/News/feed.atom", atom)
        archive.writestr("Blogger/Media/news.jpg", b"fake-jpeg-content")
    return output.getvalue()


def takeout_2018_zip() -> bytes:
    atom = '''<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom" xmlns:blogger="http://schemas.google.com/blogger/2018">
      <id>tag:blogger.com,1999:blog-2018</id><title>News</title>
      <entry>
        <id>tag:blogger.com,1999:blog-2018.post-101</id>
        <blogger:type>POST</blogger:type><blogger:status>LIVE</blogger:status>
        <author><name>Modern Author</name><uri></uri><blogger:type>BLOGGER</blogger:type></author>
        <title>Modern Takeout Story</title>
        <content type="html">&lt;p&gt;Content from the modern Blogger Takeout schema.&lt;/p&gt;&lt;img src="https://images.example.com/modern.jpg" alt="Modern"/&gt;</content>
        <blogger:metaDescription>A supplied search description.</blogger:metaDescription>
        <published>2026-06-15T10:30:00Z</published><updated>2026-06-15T11:00:00Z</updated>
        <category term="Technology" scheme="tag:blogger.com,1999:blog-2018"/>
        <blogger:filename>/2026/06/modern-takeout-story.html</blogger:filename>
        <blogger:trashed/>
      </entry>
      <entry>
        <id>tag:blogger.com,1999:blog-2018.post-102</id>
        <blogger:type>POST</blogger:type><blogger:status>DRAFT</blogger:status>
        <author><name>Modern Author</name></author><title>Private Draft</title>
        <content type="html">&lt;p&gt;This draft must not be public.&lt;/p&gt;</content>
        <published>2026-06-16T10:30:00Z</published><updated>2026-06-16T10:30:00Z</updated>
        <blogger:filename>/2026/06/private-draft.html</blogger:filename>
      </entry>
      <entry>
        <id>tag:blogger.com,1999:blog-2018.post-301</id>
        <blogger:parent>tag:blogger.com,1999:blog-2018.post-101</blogger:parent>
        <blogger:inReplyTo/><blogger:type>COMMENT</blogger:type><blogger:status>LIVE</blogger:status>
        <author><name>Modern Reader</name><uri></uri><blogger:type>ANONYMOUS</blogger:type></author>
        <content type="html">Modern comment body.</content>
        <published>2026-06-15T12:00:00Z</published><updated>2026-06-15T12:00:00Z</updated>
        <blogger:trashed/>
      </entry>
    </feed>'''
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("Takeout 2/Blogger/Blogs/News/feed.atom", atom)
        archive.writestr("Takeout 2/Blogger/Blogs/News/theme-classic.html", "templateref:rounders")
        archive.writestr("__MACOSX/Takeout 2/Blogger/Blogs/News/._theme-classic.html", b"mac metadata")
        archive.writestr("Takeout 2/Blogger/Albums/News/photo.png", b"real-png")
        archive.writestr("__MACOSX/Takeout 2/Blogger/Albums/News/._photo.png", b"mac metadata")
    return output.getvalue()


def csrf_from(response) -> str:
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.select_one('input[name="csrf"]')["value"]


def login(client: TestClient) -> None:
    page = client.get("/login")
    response = client.post(
        "/login",
        data={"username": "sainaveennews", "password": "test-admin-password-12345", "csrf": csrf_from(page)},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/admin"


def test_public_routes_do_not_require_login():
    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        assert client.head("/").status_code == 200
        assert client.head("/healthz").status_code == 200
        assert client.get("/search").status_code == 200
        assert client.get("/feed.xml").status_code == 200
        assert client.get("/sitemap.xml").status_code == 200
        assert client.get("/api/v1/articles").status_code == 200
        assert "pub-1234567890123456" in client.get("/ads.txt").text
        homepage = client.get("/")
        assert 'name="msvalidate.01" content="test-bing-verification"' in homepage.text
        assert "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" in homepage.text
        response = client.get("/admin", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/login"


def test_login_rejects_wrong_password():
    with TestClient(app) as client:
        page = client.get("/login")
        response = client.post(
            "/login",
            data={"username": "sainaveennews", "password": "not-correct-at-all", "csrf": csrf_from(page)},
        )
        assert response.status_code == 401
        assert "Invalid username or password" in response.text


def test_takeout_upload_imports_full_content_and_is_idempotent():
    with TestClient(app) as client:
        login(client)
        admin = client.get("/admin")
        response = client.post(
            "/admin/imports",
            data={"csrf": csrf_from(admin)},
            files={"archive": ("takeout.zip", takeout_zip(), "application/zip")},
            follow_redirects=False,
        )
        assert response.status_code == 303

        with SessionLocal() as session:
            job = session.scalar(select(ImportJob).order_by(ImportJob.created_at.desc()))
            assert job.status == "completed"
            assert job.posts_created == 1
            assert job.pages_created == 1
            assert job.comments_created == 1
            assert job.assets_created == 1
            article = session.scalar(select(Article).where(Article.kind == "post"))
            assert article.title == "A Test Story"
            assert article.featured_image.startswith("/media/")
            assert "script" not in article.content_html
            assert session.scalar(select(func.count()).select_from(Comment)) == 1
            assert session.scalar(select(func.count()).select_from(Asset)) == 1

        homepage = client.get("/")
        assert "A Test Story" in homepage.text
        assert "/label/World%20News" in homepage.text
        article_page = client.get("/article/a-test-story")
        assert article_page.status_code == 200
        assert "Imported body with useful reporting" in article_page.text
        assert 'href="/p/about-us"' in article_page.text
        assert "Insightful comment" in article_page.text
        assert client.get("/p/about-us").status_code == 200
        old_post = client.get("/2026/07/a-test-story.html", follow_redirects=False)
        assert old_post.status_code == 301
        assert old_post.headers["location"] == "/article/a-test-story"
        old_page = client.get("/p/about-us.html", follow_redirects=False)
        assert old_page.status_code == 301
        assert old_page.headers["location"] == "/p/about-us"
        assert client.get("/label/World%20News").status_code == 200
        assert "A Test Story" in client.get("/search?q=useful").text
        api_article = client.get("/api/v1/articles/a-test-story")
        assert api_article.status_code == 200
        assert api_article.json()["title"] == "A Test Story"
        assert "Imported body" in api_article.json()["content_html"]
        audit = build_migration_report()
        assert audit["broken_local_media"] == []
        assert audit["remaining_www_internal_links"] == 0

        admin = client.get("/admin")
        client.post(
            "/admin/imports",
            data={"csrf": csrf_from(admin)},
            files={"archive": ("takeout-again.zip", takeout_zip("Updated Story Title"), "application/zip")},
            follow_redirects=False,
        )
        with SessionLocal() as session:
            assert session.scalar(select(func.count()).select_from(Article).where(Article.kind == "post")) == 1
            assert session.scalar(select(Article).where(Article.kind == "post")).title == "Updated Story Title"


def test_modern_takeout_schema_ignores_theme_artifacts_and_links_comments():
    with SessionLocal() as session:
        session.add(
            Article(
                source_id="takeout-html:legacy-theme-artifact",
                slug="theme-classic",
                title="theme-classic",
                summary="templateref:rounders",
                content_html="templateref:rounders",
                original_url=None,
            )
        )
        session.commit()

    with TestClient(app) as client:
        login(client)
        admin = client.get("/admin")
        response = client.post(
            "/admin/imports",
            data={"csrf": csrf_from(admin)},
            files={"archive": ("takeout-2018.zip", takeout_2018_zip(), "application/zip")},
            follow_redirects=False,
        )
        assert response.status_code == 303

        with SessionLocal() as session:
            job = session.scalar(select(ImportJob).where(ImportJob.filename == "takeout-2018.zip"))
            assert job.status == "completed"
            assert job.posts_created == 2
            assert job.comments_created == 1
            assert job.assets_created == 1
            assert any("legacy theme fallback" in warning for warning in job.warnings)

            article = session.scalar(
                select(Article).where(Article.source_id == "tag:blogger.com,1999:blog-2018.post-101")
            )
            assert article.slug == "modern-takeout-story"
            assert article.original_url == "/2026/06/modern-takeout-story.html"
            assert article.summary == "A supplied search description."
            assert article.featured_image == "https://images.example.com/modern.jpg"
            assert article.labels == ["Technology"]
            assert article.is_published is True

            draft = session.scalar(
                select(Article).where(Article.source_id == "tag:blogger.com,1999:blog-2018.post-102")
            )
            assert draft.is_published is False
            assert session.scalar(select(Comment).where(Comment.article_id == article.id)).content_html == "Modern comment body."
            assert session.scalar(select(Article).where(Article.source_id == "takeout-html:legacy-theme-artifact")) is None

        homepage = client.get("/")
        assert "Modern Takeout Story" in homepage.text
        assert "Private Draft" not in homepage.text
        article_page = client.get("/article/modern-takeout-story")
        assert article_page.status_code == 200
        assert "Modern comment body" in article_page.text


def test_archive_path_traversal_is_rejected():
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("../escape.atom", "<feed/>")
    with TestClient(app) as client:
        login(client)
        admin = client.get("/admin")
        client.post(
            "/admin/imports",
            data={"csrf": csrf_from(admin)},
            files={"archive": ("unsafe.zip", output.getvalue(), "application/zip")},
            follow_redirects=False,
        )
        with SessionLocal() as session:
            job = session.scalar(select(ImportJob).where(ImportJob.filename == "unsafe.zip"))
            assert job.status == "failed"
            assert "Unsafe archive path" in job.error
