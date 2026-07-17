import math
import secrets
import uuid
import zipfile
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, quote_plus

from fastapi import BackgroundTasks, Depends, FastAPI, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import pass_context
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates

from app.config import Settings, get_settings
from app.database import SessionLocal, get_db
from app.importer import import_takeout, save_upload
from app.models import Article, Comment, ImportJob, utcnow
from app.queries import PAGE_SIZE, category_posts, count_posts, latest_posts, popular_posts, search_posts, top_labels
from app.security import clear_login_attempts, csrf_token, enforce_login_rate_limit, require_admin, verify_credentials, verify_csrf


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.imports_dir.mkdir(parents=True, exist_ok=True)
    settings.media_dir.mkdir(parents=True, exist_ok=True)
    with SessionLocal() as session:
        interrupted = list(session.scalars(select(ImportJob).where(ImportJob.status.in_(["queued", "processing"]))))
        for job in interrupted:
            job.status = "failed"
            job.stage = "Interrupted by application restart"
            job.error = "The application restarted before this import completed. Upload the archive again."
            job.completed_at = utcnow()
        session.commit()
    yield


app = FastAPI(title="IELTSTask News", docs_url=None, redoc_url=None, lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    session_cookie="news_admin_session",
    same_site="lax",
    https_only=settings.is_production,
    max_age=8 * 60 * 60,
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")
templates = Jinja2Templates(directory="app/templates")


def format_date(value: datetime | None, pattern: str = "%B %d, %Y") -> str:
    return value.strftime(pattern) if value else ""


templates.env.filters["date"] = format_date
templates.env.filters["urlencode"] = quote_plus
templates.env.filters["pathquote"] = lambda value: quote(str(value), safe="")


@app.middleware("http")
async def security_headers(request: Request, call_next):
    request.state.csp_nonce = secrets.token_urlsafe(18)
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), geolocation=(), microphone=(), payment=()")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; "
        f"script-src 'self' 'nonce-{request.state.csp_nonce}' https://www.googletagmanager.com https://pagead2.googlesyndication.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https: http:; media-src 'self' https:; "
        "frame-src https://www.youtube.com https://www.youtube-nocookie.com https://googleads.g.doubleclick.net; "
        "connect-src 'self' https://www.google-analytics.com; object-src 'none'; base-uri 'self'; frame-ancestors 'self'",
    )
    if request.url.path.startswith(("/admin", "/login")):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
    return response


def context(request: Request, session: Session, **values):
    return {
        "request": request,
        "settings": settings,
        "site_name": settings.site_name,
        "base_url": settings.app_base_url,
        "csp_nonce": request.state.csp_nonce,
        "nav_labels": top_labels(session, 9),
        "year": datetime.now(timezone.utc).year,
        **values,
    }


def page_number(value: int) -> int:
    return max(1, min(value, 100000))


@app.get("/healthz")
def health(session: Session = Depends(get_db)):
    session.execute(select(1))
    return {"status": "ok", "database": "ok"}


@app.head("/healthz")
def health_head(session: Session = Depends(get_db)):
    session.execute(select(1))
    return Response(status_code=200)


@app.head("/")
def homepage_head():
    return Response(status_code=200)


@app.get("/", response_class=HTMLResponse)
def homepage(request: Request, page: int = Query(1, ge=1), session: Session = Depends(get_db)):
    page = page_number(page)
    total = count_posts(session)
    articles = latest_posts(session, PAGE_SIZE, (page - 1) * PAGE_SIZE)
    featured = latest_posts(session, 5) if page == 1 else []
    return templates.TemplateResponse(
        request,
        "home.html",
        context(
            request,
            session,
            title="Latest News",
            articles=articles,
            featured=featured,
            popular=popular_posts(session),
            page=page,
            pages=max(1, math.ceil(total / PAGE_SIZE)),
            canonical=f"{settings.app_base_url}/" + (f"?page={page}" if page > 1 else ""),
        ),
    )


@app.get("/article/{slug}", response_class=HTMLResponse)
def article_page(slug: str, request: Request, session: Session = Depends(get_db)):
    article = session.scalar(
        select(Article).where(Article.slug == slug, Article.kind == "post", Article.is_published.is_(True))
    )
    if not article:
        raise HTTPException(status_code=404)
    article.view_count += 1
    comments = list(
        session.scalars(
            select(Comment)
            .where(Comment.article_id == article.id, Comment.is_published.is_(True))
            .order_by(Comment.published_at.asc())
        )
    )
    related = latest_posts(session, 4)
    related = [item for item in related if item.id != article.id][:3]
    session.commit()
    return templates.TemplateResponse(
        request,
        "article.html",
        context(
            request,
            session,
            title=article.title,
            description=article.summary,
            article=article,
            comments=comments,
            related=related,
            canonical=f"{settings.app_base_url}/article/{article.slug}",
        ),
    )


@app.get("/p/{slug}", response_class=HTMLResponse)
def content_page(slug: str, request: Request, session: Session = Depends(get_db)):
    article = session.scalar(
        select(Article).where(Article.slug == slug, Article.kind == "page", Article.is_published.is_(True))
    )
    if not article:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        request,
        "page.html",
        context(
            request,
            session,
            title=article.title,
            description=article.summary,
            article=article,
            canonical=f"{settings.app_base_url}/p/{article.slug}",
        ),
    )


@app.get("/label/{label}", response_class=HTMLResponse)
def label_page(label: str, request: Request, page: int = Query(1, ge=1), session: Session = Depends(get_db)):
    page = page_number(page)
    articles = category_posts(session, label, PAGE_SIZE + 1, (page - 1) * PAGE_SIZE)
    has_next = len(articles) > PAGE_SIZE
    return templates.TemplateResponse(
        request,
        "listing.html",
        context(
            request,
            session,
            title=label,
            heading=label,
            eyebrow="Category",
            articles=articles[:PAGE_SIZE],
            page=page,
            has_next=has_next,
            path=f"/label/{quote(label, safe='')}",
            popular=popular_posts(session),
            canonical=f"{settings.app_base_url}/label/{quote(label, safe='')}",
        ),
    )


@app.get("/search", response_class=HTMLResponse)
def search_page(request: Request, q: str = Query("", max_length=120), page: int = Query(1, ge=1), session: Session = Depends(get_db)):
    page = page_number(page)
    normalized = " ".join(q.split())
    articles = search_posts(session, normalized, PAGE_SIZE + 1, (page - 1) * PAGE_SIZE) if normalized else []
    return templates.TemplateResponse(
        request,
        "listing.html",
        context(
            request,
            session,
            title=f"Search: {normalized}" if normalized else "Search",
            heading=f'Results for “{normalized}”' if normalized else "Search the newsroom",
            eyebrow="Search",
            query=normalized,
            articles=articles[:PAGE_SIZE],
            page=page,
            has_next=len(articles) > PAGE_SIZE,
            path=f"/search?q={quote_plus(normalized)}",
            popular=popular_posts(session),
            canonical=f"{settings.app_base_url}/search?q={quote_plus(normalized)}" if normalized else f"{settings.app_base_url}/search",
        ),
    )


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, session: Session = Depends(get_db)):
    if request.session.get("admin") is True:
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse(
        request,
        "login.html",
        context(request, session, title="Admin sign in", csrf=csrf_token(request), canonical=None),
    )


@app.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    username: str = Form(..., max_length=255),
    password: str = Form(..., max_length=1024),
    csrf: str = Form(...),
    session: Session = Depends(get_db),
):
    verify_csrf(request, csrf)
    enforce_login_rate_limit(request)
    if not verify_credentials(username, password, settings):
        return templates.TemplateResponse(
            request,
            "login.html",
            context(request, session, title="Admin sign in", csrf=csrf_token(request), error="Invalid username or password", canonical=None),
            status_code=401,
        )
    clear_login_attempts(request)
    request.session.clear()
    request.session["admin"] = True
    csrf_token(request)
    return RedirectResponse("/admin", status_code=303)


@app.post("/logout")
def logout(request: Request, csrf: str = Form(...)):
    require_admin(request)
    verify_csrf(request, csrf)
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, session: Session = Depends(get_db)):
    require_admin(request)
    jobs = list(session.scalars(select(ImportJob).order_by(ImportJob.created_at.desc()).limit(20)))
    counts = {
        "articles": session.scalar(select(func.count()).select_from(Article).where(Article.kind == "post")) or 0,
        "pages": session.scalar(select(func.count()).select_from(Article).where(Article.kind == "page")) or 0,
        "comments": session.scalar(select(func.count()).select_from(Comment)) or 0,
    }
    return templates.TemplateResponse(
        request,
        "admin.html",
        context(request, session, title="Takeout importer", csrf=csrf_token(request), jobs=jobs, counts=counts, canonical=None),
    )


@app.post("/admin/imports")
def create_import(
    request: Request,
    background_tasks: BackgroundTasks,
    archive: UploadFile,
    csrf: str = Form(...),
    session: Session = Depends(get_db),
):
    require_admin(request)
    verify_csrf(request, csrf)
    filename = Path(archive.filename or "takeout.zip").name
    if not filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Upload a Google Takeout ZIP file")
    job = ImportJob(filename=filename)
    session.add(job)
    session.commit()
    destination = settings.imports_dir / f"{job.id}.zip"
    try:
        save_upload(archive, destination, settings.upload_limit_bytes)
        if not zipfile.is_zipfile(destination):
            raise ValueError("The uploaded file is not a valid ZIP archive")
    except ValueError as exc:
        destination.unlink(missing_ok=True)
        job.status = "failed"
        job.stage = "Upload rejected"
        job.error = str(exc)
        job.completed_at = utcnow()
        session.commit()
        return RedirectResponse(f"/admin?upload_error={quote_plus(str(exc))}", status_code=303)
    background_tasks.add_task(import_takeout, job.id, destination)
    return RedirectResponse(f"/admin#import-{job.id}", status_code=303)


@app.get("/admin/imports/{job_id}")
def import_status(job_id: uuid.UUID, request: Request, session: Session = Depends(get_db)):
    require_admin(request)
    job = session.get(ImportJob, job_id)
    if not job:
        raise HTTPException(status_code=404)
    return JSONResponse(
        {
            "id": str(job.id),
            "status": job.status,
            "progress": job.progress,
            "stage": job.stage,
            "posts_created": job.posts_created,
            "posts_updated": job.posts_updated,
            "pages_created": job.pages_created,
            "comments_created": job.comments_created,
            "assets_created": job.assets_created,
            "warnings": job.warnings,
            "error": job.error,
        }
    )


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots():
    return f"User-agent: *\nAllow: /\nDisallow: /admin\nDisallow: /login\nSitemap: {settings.app_base_url}/sitemap.xml\n"


@app.get("/sitemap.xml")
def sitemap(session: Session = Depends(get_db)):
    articles = list(session.scalars(select(Article).where(Article.is_published.is_(True)).order_by(Article.updated_at.desc())))
    urls = [f"<url><loc>{settings.app_base_url}/</loc></url>"]
    for article in articles:
        route = "p" if article.kind == "page" else "article"
        urls.append(
            f"<url><loc>{settings.app_base_url}/{route}/{article.slug}</loc><lastmod>{article.updated_at.date().isoformat()}</lastmod></url>"
        )
    return Response("<?xml version=\"1.0\" encoding=\"UTF-8\"?><urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">" + "".join(urls) + "</urlset>", media_type="application/xml")


@app.get("/feed.xml")
def feed(session: Session = Depends(get_db)):
    articles = latest_posts(session, 20)
    items = "".join(
        f"<item><title><![CDATA[{article.title}]]></title><link>{settings.app_base_url}/article/{article.slug}</link>"
        f"<guid>{settings.app_base_url}/article/{article.slug}</guid><pubDate>{article.published_at:%a, %d %b %Y %H:%M:%S %z}</pubDate>"
        f"<description><![CDATA[{article.summary}]]></description></item>"
        for article in articles
    )
    xml = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?><rss version=\"2.0\"><channel><title>{settings.site_name}</title><link>{settings.app_base_url}</link><description>Independent news and analysis</description>{items}</channel></rss>"
    return Response(xml, media_type="application/rss+xml")


@app.exception_handler(404)
def not_found(request: Request, _):
    with SessionLocal() as session:
        return templates.TemplateResponse(
            request,
            "404.html",
            context(request, session, title="Page not found", canonical=None),
            status_code=404,
        )
