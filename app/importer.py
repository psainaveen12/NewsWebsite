import hashlib
import html
import mimetypes
import re
import stat
import threading
import unicodedata
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse, urlunsplit

import bleach
from bleach.css_sanitizer import CSSSanitizer
from bs4 import BeautifulSoup
from dateutil.parser import isoparse
from defusedxml import ElementTree
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.integrations import submit_indexnow
from app.models import Article, Asset, Comment, ImportJob, utcnow


IMPORT_LOCK = threading.Lock()
IMAGE_EXTENSIONS = {".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
ASSET_EXTENSIONS = IMAGE_EXTENSIONS | {
    ".aac", ".csv", ".doc", ".docx", ".m4a", ".mov", ".mp3", ".mp4", ".mpeg", ".ogg", ".ogv",
    ".pdf", ".ppt", ".pptx", ".txt", ".wav", ".webm", ".xls", ".xlsx", ".zip",
}
ALLOWED_TAGS = {
    "a", "abbr", "b", "blockquote", "br", "caption", "cite", "code", "del", "div", "em",
    "figcaption", "figure", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "iframe", "img",
    "li", "mark", "ol", "p", "pre", "q", "s", "small", "span", "strong", "sub", "sup", "table",
    "tbody", "td", "tfoot", "th", "thead", "tr", "u", "ul",
}
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
    "blockquote": ["cite"],
    "div": ["class", "style"],
    "figure": ["class"],
    "iframe": ["src", "title", "width", "height", "allow", "allowfullscreen", "loading", "referrerpolicy"],
    "img": ["src", "alt", "title", "width", "height", "loading", "decoding", "class"],
    "ol": ["start"],
    "span": ["class", "style"],
    "td": ["colspan", "rowspan"],
    "th": ["colspan", "rowspan", "scope"],
}
CSS_SANITIZER = CSSSanitizer(
    allowed_css_properties=["color", "background-color", "font-weight", "font-style", "text-align", "text-decoration"]
)


@dataclass
class ParsedEntry:
    source_id: str
    kind: str
    title: str
    content: str
    summary: str
    author: str
    author_url: str | None
    avatar_url: str | None
    original_url: str | None
    published_at: datetime
    updated_at: datetime
    labels: list[str]
    is_published: bool
    reply_ref: str | None = None
    reply_href: str | None = None


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _children(element, name: str):
    return [child for child in list(element) if _local_name(child.tag) == name]


def _first(element, name: str):
    matches = _children(element, name)
    return matches[0] if matches else None


def _text(element, name: str, default: str = "") -> str:
    child = _first(element, name)
    return "".join(child.itertext()).strip() if child is not None else default


def _date(value: str | None, default: datetime | None = None) -> datetime:
    if not value:
        return default or utcnow()
    try:
        parsed = isoparse(value)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError, OverflowError):
        return default or utcnow()


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return slug[:220] or "article"


def _unique_slug(session: Session, requested: str, article_id: int | None = None) -> str:
    base = requested[:220] or "article"
    candidate = base
    suffix = 2
    while True:
        found = session.scalar(select(Article).where(Article.slug == candidate))
        if not found or found.id == article_id:
            return candidate
        candidate = f"{base[:210]}-{suffix}"
        suffix += 1


def _safe_member_name(name: str) -> str:
    decoded = unquote(name.replace("\\", "/"))
    path = PurePosixPath(decoded)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"Unsafe archive path: {name}")
    return path.as_posix()


def _is_metadata_member(name: str) -> bool:
    path = PurePosixPath(name.replace("\\", "/"))
    return "__MACOSX" in path.parts or path.name.startswith("._") or path.name == ".DS_Store"


def _validate_archive(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    settings = get_settings()
    infos = archive.infolist()
    if len(infos) > settings.max_archive_files:
        raise ValueError(f"Archive contains more than {settings.max_archive_files} files")
    total_size = 0
    for info in infos:
        _safe_member_name(info.filename)
        mode = info.external_attr >> 16
        if stat.S_ISLNK(mode):
            raise ValueError("Archive symbolic links are not allowed")
        total_size += info.file_size
        if total_size > settings.archive_limit_bytes:
            raise ValueError("Archive expands beyond the configured safety limit")
        if info.compress_size and info.file_size / info.compress_size > 5000:
            raise ValueError(f"Suspicious compression ratio in {info.filename}")
    return infos


def _progress(session: Session, job: ImportJob, value: int, stage: str) -> None:
    job.progress = max(0, min(value, 100))
    job.stage = stage[:255]
    session.commit()


def _store_assets(
    session: Session,
    job: ImportJob,
    archive: zipfile.ZipFile,
    infos: list[zipfile.ZipInfo],
) -> tuple[dict[str, str], dict[str, str]]:
    settings = get_settings()
    asset_dir = settings.media_dir / str(job.id)
    asset_dir.mkdir(parents=True, exist_ok=True)
    by_path: dict[str, str] = {}
    by_basename: dict[str, str] = {}
    basename_counts: dict[str, int] = {}
    asset_infos = [
        info
        for info in infos
        if not info.is_dir()
        and not _is_metadata_member(info.filename)
        and Path(info.filename).suffix.lower() in ASSET_EXTENSIONS
    ]

    for index, info in enumerate(asset_infos, start=1):
        safe_name = _safe_member_name(info.filename)
        basename = PurePosixPath(safe_name).name
        basename_counts[basename.lower()] = basename_counts.get(basename.lower(), 0) + 1
        digest = hashlib.sha256()
        temporary = asset_dir / f".{uuid.uuid4().hex}.part"
        size_bytes = 0
        with archive.open(info) as source, temporary.open("wb") as target:
            while chunk := source.read(1024 * 1024):
                digest.update(chunk)
                target.write(chunk)
                size_bytes += len(chunk)
        checksum = digest.hexdigest()
        existing = session.scalar(select(Asset).where(Asset.checksum == checksum))
        if existing:
            public_path = existing.public_path
            temporary.unlink(missing_ok=True)
        else:
            extension = Path(basename).suffix.lower()
            stored_name = f"{checksum[:24]}{extension}"
            target = asset_dir / stored_name
            temporary.replace(target)
            public_path = f"/media/{job.id}/{stored_name}"
            media_type = mimetypes.guess_type(basename)[0] or "application/octet-stream"
            session.add(
                Asset(
                    original_name=basename,
                    original_path=safe_name,
                    public_path=public_path,
                    media_type=media_type,
                    checksum=checksum,
                    size_bytes=size_bytes,
                )
            )
            session.flush()
            job.assets_created += 1
        by_path[safe_name.lower()] = public_path
        by_basename[basename.lower()] = public_path
        if index % 50 == 0:
            session.commit()

    ambiguous = {name for name, count in basename_counts.items() if count > 1}
    for name in ambiguous:
        by_basename.pop(name, None)
    session.commit()
    return by_path, by_basename


def _asset_url(value: str, by_path: dict[str, str], by_basename: dict[str, str]) -> str:
    if not value or value.startswith(("data:", "blob:")):
        return value
    parsed = urlparse(value)
    candidate = unquote(parsed.path or value).replace("\\", "/").lstrip("./").lower()
    if candidate in by_path:
        return by_path[candidate]
    basename = PurePosixPath(candidate).name.lower()
    return by_basename.get(basename, value)


def sanitize_content(raw_html: str, by_path: dict[str, str], by_basename: dict[str, str]) -> tuple[str, str | None]:
    soup = BeautifulSoup(raw_html or "", "html.parser")
    for tag in soup.find_all(["script", "style", "object", "embed", "form", "input", "button"]):
        tag.decompose()
    for iframe in soup.find_all("iframe"):
        host = (urlparse(iframe.get("src", "")).hostname or "").lower()
        if host not in {"youtube.com", "www.youtube.com", "youtube-nocookie.com", "www.youtube-nocookie.com"}:
            iframe.decompose()
            continue
        iframe["loading"] = "lazy"
        iframe["referrerpolicy"] = "strict-origin-when-cross-origin"
        iframe["title"] = iframe.get("title") or "Embedded video"
    first_image: str | None = None
    for image in soup.find_all("img"):
        rewritten = _asset_url(image.get("src", ""), by_path, by_basename)
        if not rewritten:
            image.decompose()
            continue
        image["src"] = rewritten
        image["loading"] = "lazy"
        image["decoding"] = "async"
        image["alt"] = image.get("alt") or ""
        first_image = first_image or rewritten
    for anchor in soup.find_all("a"):
        href = anchor.get("href", "")
        anchor["href"] = _asset_url(href, by_path, by_basename)
        anchor["rel"] = "noopener noreferrer"
        if anchor.get("target") == "_blank":
            anchor["rel"] = "noopener noreferrer"
    cleaned = bleach.clean(
        str(soup),
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols={"http", "https", "mailto"},
        css_sanitizer=CSS_SANITIZER,
        strip=True,
    )
    return cleaned, first_image


def _entry_kind(entry) -> str | None:
    modern_type = _text(entry, "type").strip().lower()
    if modern_type in {"post", "page", "comment"}:
        return modern_type
    terms = [category.attrib.get("term", "") for category in _children(entry, "category")]
    for kind in ("post", "page", "comment"):
        if any(term.endswith(f"kind#{kind}") for term in terms):
            return kind
    return None


def _parse_entry(entry) -> ParsedEntry | None:
    kind = _entry_kind(entry)
    if not kind:
        return None
    source_id = _text(entry, "id")
    content = _text(entry, "content")
    if not source_id:
        source_id = "generated:" + hashlib.sha256(content.encode()).hexdigest()
    links = _children(entry, "link")
    original_url = next((link.attrib.get("href") for link in links if link.attrib.get("rel") == "alternate"), None)
    original_url = original_url or _text(entry, "filename") or None
    author_node = _first(entry, "author")
    author = _text(author_node, "name", "Editorial Desk") if author_node is not None else "Editorial Desk"
    author_url = _text(author_node, "uri") if author_node is not None else None
    avatar = None
    if author_node is not None:
        avatar_node = next((node for node in list(author_node) if _local_name(node.tag) == "image"), None)
        avatar = avatar_node.attrib.get("src") if avatar_node is not None else None
    published = _date(_text(entry, "published"))
    updated = _date(_text(entry, "updated"), published)
    labels = []
    for category in _children(entry, "category"):
        term = category.attrib.get("term", "").strip()
        scheme = category.attrib.get("scheme", "")
        if term and "kind#" not in term and "schemas.google.com" not in scheme:
            labels.append(term)
    draft = next((node for node in entry.iter() if _local_name(node.tag) == "draft"), None)
    is_draft = draft is not None and (draft.text or "").strip().lower() in {"yes", "true", "1"}
    modern_status = _text(entry, "status").strip().upper()
    trashed = _text(entry, "trashed").strip().lower() in {"yes", "true", "1"}
    is_published = not is_draft and not trashed and modern_status not in {"DRAFT", "SCHEDULED", "TRASHED"}
    reply = next((node for node in entry.iter() if _local_name(node.tag) == "in-reply-to"), None)
    parent_ref = _text(entry, "parent")
    if reply is not None and not parent_ref:
        parent_ref = (reply.text or "").strip()
    return ParsedEntry(
        source_id=source_id,
        kind=kind,
        title=html.unescape(_text(entry, "title") or "Untitled"),
        content=content,
        summary=_text(entry, "summary") or _text(entry, "metaDescription"),
        author=author or "Editorial Desk",
        author_url=author_url or None,
        avatar_url=avatar,
        original_url=original_url,
        published_at=published,
        updated_at=updated,
        labels=list(dict.fromkeys(labels)),
        is_published=is_published,
        reply_ref=parent_ref or (reply.attrib.get("ref") if reply is not None else None),
        reply_href=reply.attrib.get("href") if reply is not None else None,
    )


def _parse_xml_members(archive: zipfile.ZipFile, infos: list[zipfile.ZipInfo], warnings: list[str]) -> list[ParsedEntry]:
    entries: list[ParsedEntry] = []
    xml_infos = [
        i
        for i in infos
        if not i.is_dir()
        and not _is_metadata_member(i.filename)
        and Path(i.filename).suffix.lower() in {".atom", ".xml"}
    ]
    for info in xml_infos:
        try:
            with archive.open(info) as stream:
                for _, node in ElementTree.iterparse(stream, events=("end",)):
                    if _local_name(node.tag) == "entry":
                        parsed = _parse_entry(node)
                        if parsed:
                            entries.append(parsed)
                        node.clear()
        except Exception as exc:
            if len(warnings) < 100:
                warnings.append(f"Skipped XML file {info.filename}: {type(exc).__name__}")
    return entries


def _parse_html_fallback(archive: zipfile.ZipFile, infos: list[zipfile.ZipInfo]) -> list[ParsedEntry]:
    entries: list[ParsedEntry] = []
    for info in infos:
        if (
            info.is_dir()
            or _is_metadata_member(info.filename)
            or Path(info.filename).suffix.lower() not in {".html", ".htm"}
            or PurePosixPath(info.filename).name.lower().startswith("theme-")
        ):
            continue
        raw = archive.read(info).decode("utf-8", errors="replace")
        soup = BeautifulSoup(raw, "html.parser")
        title_node = soup.find("h1") or soup.find("title")
        title = title_node.get_text(" ", strip=True) if title_node else Path(info.filename).stem
        published_meta = soup.find("meta", attrs={"property": "article:published_time"})
        author_meta = soup.find("meta", attrs={"name": "author"})
        canonical = soup.find("link", attrs={"rel": "canonical"})
        body = soup.find("article") or soup.find("main") or soup.body
        if body is None or len(body.get_text(" ", strip=True)) < 40:
            continue
        source_id = "takeout-html:" + hashlib.sha256(_safe_member_name(info.filename).encode()).hexdigest()
        entries.append(
            ParsedEntry(
                source_id=source_id,
                kind="post",
                title=title or "Untitled",
                content=str(body),
                summary="",
                author=author_meta.get("content", "Editorial Desk") if author_meta else "Editorial Desk",
                author_url=None,
                avatar_url=None,
                original_url=canonical.get("href") if canonical else None,
                published_at=_date(published_meta.get("content") if published_meta else None),
                updated_at=_date(published_meta.get("content") if published_meta else None),
                labels=[],
                is_published=True,
            )
        )
    return entries


def _summary(entry: ParsedEntry, content_html: str) -> str:
    supplied = BeautifulSoup(entry.summary, "html.parser").get_text(" ", strip=True)
    text = supplied or BeautifulSoup(content_html, "html.parser").get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text)[:280]


def _slug_from_entry(entry: ParsedEntry) -> str:
    if entry.original_url:
        stem = Path(urlparse(entry.original_url).path).stem
        if stem and stem not in {"index", ""}:
            return slugify(stem)
    return slugify(entry.title)


def _remove_legacy_takeout_artifacts(session: Session) -> int:
    candidates = session.scalars(select(Article).where(Article.source_id.like("takeout-html:%")))
    removed = 0
    for article in candidates:
        title = article.title.strip().lower().removeprefix("._")
        if article.original_url is None and title == "theme-classic":
            session.delete(article)
            removed += 1
    if removed:
        session.commit()
    return removed


def _upsert_articles(
    session: Session,
    job: ImportJob,
    entries: list[ParsedEntry],
    by_path: dict[str, str],
    by_basename: dict[str, str],
) -> tuple[dict[str, Article], dict[str, Article]]:
    by_source: dict[str, Article] = {}
    by_url: dict[str, Article] = {}
    content_entries = [entry for entry in entries if entry.kind in {"post", "page"}]
    for index, entry in enumerate(content_entries, start=1):
        cleaned, featured_image = sanitize_content(entry.content, by_path, by_basename)
        existing = session.scalar(select(Article).where(Article.source_id == entry.source_id))
        if existing:
            article = existing
            job.posts_updated += 1
        else:
            article = Article(
                source_id=entry.source_id,
                slug=_unique_slug(session, _slug_from_entry(entry)),
                title=entry.title,
                kind=entry.kind,
            )
            session.add(article)
            session.flush()
            if entry.kind == "page":
                job.pages_created += 1
            else:
                job.posts_created += 1
        article.title = entry.title[:500]
        article.kind = entry.kind
        article.summary = _summary(entry, cleaned)
        article.content_html = cleaned
        article.author_name = entry.author[:255]
        article.original_url = entry.original_url
        article.featured_image = featured_image
        article.labels = entry.labels
        article.metadata_json = {"takeout_source_id": entry.source_id}
        article.is_published = entry.is_published
        article.published_at = entry.published_at
        article.updated_at = entry.updated_at
        by_source[entry.source_id] = article
        if entry.original_url:
            by_url[entry.original_url] = article
        if index % 100 == 0:
            session.commit()
    session.commit()
    return by_source, by_url


def _rewrite_internal_links(session: Session, imported: list[Article]) -> None:
    settings = get_settings()
    targets: dict[str, str] = {}
    for article in session.scalars(select(Article).where(Article.original_url.is_not(None))):
        source_path = urlparse(article.original_url or "").path
        if source_path:
            route = "p" if article.kind == "page" else "article"
            targets[source_path.rstrip("/") or "/"] = f"/{route}/{article.slug}"

    internal_hosts = {"ieltstask.com", "www.ieltstask.com", settings.app_domain.lower()}
    for article in imported:
        soup = BeautifulSoup(article.content_html, "html.parser")
        changed = False
        for anchor in soup.find_all("a", href=True):
            parsed = urlparse(anchor["href"])
            if parsed.hostname and parsed.hostname.lower() not in internal_hosts:
                continue
            target = targets.get((parsed.path.rstrip("/") or "/"))
            if target:
                anchor["href"] = urlunsplit(("", "", target, parsed.query, parsed.fragment))
                changed = True
        if changed:
            article.content_html = str(soup)
    session.commit()


def _link_assets_to_articles(session: Session, imported: list[Article]) -> None:
    unlinked = {
        asset.public_path: asset
        for asset in session.scalars(select(Asset).where(Asset.article_id.is_(None)))
    }
    for article in imported:
        soup = BeautifulSoup(article.content_html, "html.parser")
        for node in soup.find_all(["img", "a"]):
            path = node.get("src") or node.get("href")
            if path in unlinked:
                unlinked[path].article_id = article.id
    session.commit()


def _upsert_comments(
    session: Session,
    job: ImportJob,
    entries: list[ParsedEntry],
    by_source: dict[str, Article],
    by_url: dict[str, Article],
    by_path: dict[str, str],
    by_basename: dict[str, str],
) -> None:
    comment_targets: dict[str, Article] = {}
    for entry in [item for item in entries if item.kind == "comment"]:
        article = by_source.get(entry.reply_ref or "") or by_url.get(entry.reply_href or "") or comment_targets.get(entry.reply_ref or "")
        if not article:
            if len(job.warnings) < 100:
                job.warnings = [*job.warnings, f"Comment {entry.source_id} has no matching post"]
            continue
        comment_targets[entry.source_id] = article
        existing = session.scalar(select(Comment).where(Comment.source_id == entry.source_id))
        cleaned, _ = sanitize_content(entry.content, by_path, by_basename)
        if existing:
            comment = existing
        else:
            comment = Comment(
                article_id=article.id,
                source_id=entry.source_id,
            )
            session.add(comment)
            job.comments_created += 1
        comment.article_id = article.id
        comment.author_name = entry.author[:255]
        comment.author_url = entry.author_url
        comment.avatar_url = entry.avatar_url
        comment.content_html = cleaned
        comment.published_at = entry.published_at
        comment.is_published = entry.is_published
    session.commit()


def import_takeout(job_id: uuid.UUID, archive_path: Path) -> None:
    with IMPORT_LOCK, SessionLocal() as session:
        job = session.get(ImportJob, job_id)
        if not job:
            return
        try:
            job.status = "processing"
            job.started_at = utcnow()
            _progress(session, job, 3, "Validating archive")
            with zipfile.ZipFile(archive_path) as archive:
                infos = _validate_archive(archive)
                _progress(session, job, 12, "Securing and indexing media")
                by_path, by_basename = _store_assets(session, job, archive, infos)
                _progress(session, job, 38, "Reading Blogger export")
                warnings: list[str] = []
                entries = _parse_xml_members(archive, infos, warnings)
                if not any(entry.kind in {"post", "page"} for entry in entries):
                    warnings.append("No Blogger Atom posts found; used HTML fallback")
                    entries.extend(_parse_html_fallback(archive, infos))
                if not any(entry.kind in {"post", "page"} for entry in entries):
                    raise ValueError("No Blogger posts or pages were found in this Takeout archive")
                removed_artifacts = _remove_legacy_takeout_artifacts(session)
                if removed_artifacts:
                    warnings.append(f"Removed {removed_artifacts} legacy theme fallback artifacts")
                job.warnings = warnings[:100]
                session.commit()
                _progress(session, job, 58, "Importing posts and pages")
                by_source, by_url = _upsert_articles(session, job, entries, by_path, by_basename)
                imported_articles = list(by_source.values())
                _rewrite_internal_links(session, imported_articles)
                _link_assets_to_articles(session, imported_articles)
                _progress(session, job, 82, "Linking comments")
                _upsert_comments(session, job, entries, by_source, by_url, by_path, by_basename)
            job.status = "completed"
            job.progress = 100
            job.stage = "Import complete"
            job.completed_at = utcnow()
            session.commit()
            submit_indexnow(
                [
                    f"{get_settings().app_base_url}/{'p' if article.kind == 'page' else 'article'}/{article.slug}"
                    for article in by_source.values()
                    if article.is_published
                ]
            )
        except Exception as exc:
            session.rollback()
            job = session.get(ImportJob, job_id)
            if job:
                job.status = "failed"
                job.stage = "Import failed"
                job.error = str(exc)[:4000]
                job.completed_at = utcnow()
                session.commit()
        finally:
            archive_path.unlink(missing_ok=True)


def save_upload(upload, destination: Path, limit_bytes: int) -> int:
    written = 0
    with destination.open("wb") as target:
        while chunk := upload.file.read(1024 * 1024):
            written += len(chunk)
            if written > limit_bytes:
                target.close()
                destination.unlink(missing_ok=True)
                raise ValueError("Upload exceeds the configured size limit")
            target.write(chunk)
    return written
