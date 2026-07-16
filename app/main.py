from __future__ import annotations

import asyncio
import math
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config import Settings
from app.database import build_engine, database_is_healthy, initialize_database
from app.metadata import ArticleMetadata, MetadataFetchError, fetch_article_metadata
from app.models import Article
from app.security import (
    LoginThrottle,
    authenticate_session,
    clear_session,
    credentials_match,
    csrf_is_valid,
    csrf_token,
    is_admin,
)
from app.services import public_articles, save_article_metadata


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def format_date(value: datetime | None) -> str:
    return value.strftime("%B %d, %Y") if value else "Recently added"


templates.env.filters["display_date"] = format_date


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    engine = build_engine(settings)

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        await asyncio.to_thread(
            initialize_database,
            engine,
            20,
            1.5,
            settings.environment != "production",
        )
        yield
        engine.dispose()

    application = FastAPI(
        title=settings.app_name,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )
    application.state.settings = settings
    application.state.engine = engine
    application.state.metadata_fetcher = fetch_article_metadata
    application.state.login_throttle = LoginThrottle()
    application.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret,
        session_cookie="news_admin_session",
        max_age=28_800,
        same_site="strict",
        https_only=settings.cookie_secure,
    )
    application.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_host_list)
    application.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

    @application.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data: https:; "
            "style-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'",
        )
        return response

    def render(
        request: Request,
        template_name: str,
        context: dict | None = None,
        status_code: int = 200,
    ) -> HTMLResponse:
        values = {
            "request": request,
            "app_name": settings.app_name,
            "is_admin": is_admin(request),
            "csrf_token": csrf_token(request),
        }
        values.update(context or {})
        return templates.TemplateResponse(
            request=request,
            name=template_name,
            context=values,
            status_code=status_code,
        )

    def recent_articles(session: Session) -> list[Article]:
        return list(
            session.scalars(select(Article).order_by(Article.created_at.desc()).limit(15))
        )

    @application.get("/", response_class=HTMLResponse)
    def home(request: Request, q: str = "", page: int = Query(default=1, ge=1, le=10_000)):
        query = q.strip()[:120]
        current_page = max(page, 1)
        with Session(engine) as session:
            articles, total = public_articles(session, query, current_page, settings.page_size)
        page_count = max(1, math.ceil(total / settings.page_size))
        if current_page > page_count:
            current_page = page_count
            with Session(engine) as session:
                articles, total = public_articles(session, query, current_page, settings.page_size)
        return render(
            request,
            "home.html",
            {
                "articles": articles,
                "query": query,
                "page": current_page,
                "page_count": page_count,
                "total": total,
            },
        )

    @application.get("/articles/{slug}", response_class=HTMLResponse)
    def article_page(request: Request, slug: str):
        with Session(engine) as session:
            article = session.scalar(
                select(Article).where(Article.slug == slug, Article.is_published.is_(True))
            )
        if not article:
            return render(request, "404.html", status_code=404)
        return render(request, "article.html", {"article": article})

    @application.get("/login", response_class=HTMLResponse)
    def login_page(request: Request):
        if is_admin(request):
            return RedirectResponse("/admin", status_code=303)
        return render(request, "login.html", {"error": None})

    @application.post("/login", response_class=HTMLResponse)
    def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        csrf: str = Form(...),
    ):
        if not csrf_is_valid(request, csrf):
            return render(request, "login.html", {"error": "Your session expired. Try again."}, 400)

        throttle: LoginThrottle = application.state.login_throttle
        client_key = request.client.host if request.client else "unknown"
        if not throttle.is_allowed(client_key):
            return render(
                request,
                "login.html",
                {"error": "Too many attempts. Try again in 15 minutes."},
                429,
            )

        if not credentials_match(username.strip(), password, settings):
            throttle.record_failure(client_key)
            return render(request, "login.html", {"error": "Invalid username or password."}, 401)

        throttle.clear(client_key)
        authenticate_session(request)
        return RedirectResponse("/admin", status_code=303)

    @application.post("/logout")
    def logout(request: Request, csrf: str = Form(...)):
        if not csrf_is_valid(request, csrf):
            return JSONResponse({"detail": "Invalid CSRF token"}, status_code=400)
        clear_session(request)
        return RedirectResponse("/", status_code=303)

    @application.get("/admin", response_class=HTMLResponse)
    def admin_page(request: Request):
        if not is_admin(request):
            return RedirectResponse("/login", status_code=303)
        with Session(engine) as session:
            articles = recent_articles(session)
        return render(request, "admin.html", {"articles": articles, "results": [], "error": None})

    @application.post("/admin/articles/import", response_class=HTMLResponse)
    async def import_articles(
        request: Request,
        urls: str = Form(...),
        csrf: str = Form(...),
    ):
        if not is_admin(request):
            return RedirectResponse("/login", status_code=303)
        if not csrf_is_valid(request, csrf):
            return JSONResponse({"detail": "Invalid CSRF token"}, status_code=400)

        if len(urls) > 50_000:
            with Session(engine) as session:
                articles = recent_articles(session)
            return render(
                request,
                "admin.html",
                {"articles": articles, "results": [], "error": "The submitted URL list is too large."},
                413,
            )

        submitted_urls = list(dict.fromkeys(line.strip() for line in urls.splitlines() if line.strip()))
        if not submitted_urls:
            with Session(engine) as session:
                articles = recent_articles(session)
            return render(
                request,
                "admin.html",
                {"articles": articles, "results": [], "error": "Enter at least one URL."},
                400,
            )
        if len(submitted_urls) > settings.max_import_urls:
            with Session(engine) as session:
                articles = recent_articles(session)
            return render(
                request,
                "admin.html",
                {
                    "articles": articles,
                    "results": [],
                    "error": f"Submit no more than {settings.max_import_urls} URLs at once.",
                },
                400,
            )

        semaphore = asyncio.Semaphore(settings.fetch_concurrency)

        async def fetch_one(source_url: str) -> tuple[str, ArticleMetadata | None, str | None]:
            async with semaphore:
                try:
                    metadata = await application.state.metadata_fetcher(source_url, settings)
                    return source_url, metadata, None
                except MetadataFetchError as exc:
                    return source_url, None, str(exc)
                except Exception:
                    return source_url, None, "Unexpected fetch error"

        fetched = await asyncio.gather(*(fetch_one(source_url) for source_url in submitted_urls))
        results: list[dict[str, str]] = []
        with Session(engine) as session:
            for source_url, metadata, error in fetched:
                if error or not metadata:
                    results.append({"url": source_url, "status": "failed", "message": error or "Failed"})
                    continue
                try:
                    saved = save_article_metadata(session, metadata)
                    session.commit()
                    results.append(
                        {
                            "url": source_url,
                            "status": "success",
                            "message": f"{saved.action.title()}: {saved.article.title}",
                        }
                    )
                except SQLAlchemyError:
                    session.rollback()
                    results.append(
                        {"url": source_url, "status": "failed", "message": "Database save failed"}
                    )
            articles = recent_articles(session)

        return render(
            request,
            "admin.html",
            {"articles": articles, "results": results, "error": None},
        )

    @application.get("/healthz")
    def health():
        healthy = database_is_healthy(engine)
        return JSONResponse(
            {"status": "ok" if healthy else "unhealthy", "database": "ok" if healthy else "down"},
            status_code=200 if healthy else 503,
        )

    return application


app = create_app()
