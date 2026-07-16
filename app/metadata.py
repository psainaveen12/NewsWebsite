from __future__ import annotations

import asyncio
import html
import ipaddress
import re
import socket
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit, urlunsplit

import httpx
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from app.config import Settings


class MetadataFetchError(ValueError):
    pass


@dataclass(slots=True)
class ArticleMetadata:
    source_url: str
    canonical_url: str
    title: str
    description: str | None
    image_url: str | None
    author: str | None
    source_name: str | None
    source_domain: str
    published_at: datetime | None
    raw_metadata: dict[str, str | None]


def normalize_http_url(value: str) -> str:
    value = value.strip()
    if not value:
        raise MetadataFetchError("URL is empty")

    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise MetadataFetchError("URL has an invalid host or port") from exc

    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"}:
        raise MetadataFetchError("Only http and https URLs are allowed")
    if not parsed.hostname:
        raise MetadataFetchError("URL must include a hostname")
    if parsed.username or parsed.password:
        raise MetadataFetchError("URLs containing credentials are not allowed")

    hostname = parsed.hostname.rstrip(".").lower()
    if hostname == "localhost" or hostname.endswith(".localhost") or hostname.endswith(".local"):
        raise MetadataFetchError("Local network URLs are not allowed")

    host_for_netloc = f"[{hostname}]" if ":" in hostname else hostname
    default_port = 80 if scheme == "http" else 443
    netloc = host_for_netloc if port in (None, default_port) else f"{host_for_netloc}:{port}"
    path = parsed.path or "/"
    return urlunsplit((scheme, netloc, path, parsed.query, ""))


async def ensure_public_url(value: str) -> str:
    normalized = normalize_http_url(value)
    parsed = urlsplit(normalized)
    hostname = parsed.hostname or ""

    try:
        literal_ip = ipaddress.ip_address(hostname)
        addresses = [literal_ip]
    except ValueError:
        try:
            loop = asyncio.get_running_loop()
            records = await loop.getaddrinfo(
                hostname,
                parsed.port or (443 if parsed.scheme == "https" else 80),
                type=socket.SOCK_STREAM,
            )
        except socket.gaierror as exc:
            raise MetadataFetchError("Hostname could not be resolved") from exc
        addresses = list({ipaddress.ip_address(record[4][0]) for record in records})

    if not addresses or any(not address.is_global for address in addresses):
        raise MetadataFetchError("Private or reserved network addresses are not allowed")
    return normalized


def _clean_text(value: str | None, maximum_length: int) -> str | None:
    if not value:
        return None
    cleaned = re.sub(r"\s+", " ", html.unescape(value)).strip()
    return cleaned[:maximum_length] or None


def _metadata_map(soup: BeautifulSoup) -> dict[str, str]:
    values: dict[str, str] = {}
    for tag in soup.find_all("meta"):
        key = tag.get("property") or tag.get("name") or tag.get("itemprop")
        content = tag.get("content")
        if key and content:
            values[str(key).strip().lower()] = str(content).strip()
    return values


def _first(values: dict[str, str], *keys: str) -> str | None:
    for key in keys:
        value = values.get(key.lower())
        if value:
            return value
    return None


def _parse_published_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = date_parser.parse(value)
    except (ValueError, OverflowError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


async def fetch_article_metadata(url: str, settings: Settings) -> ArticleMetadata:
    current_url = await ensure_public_url(url)
    original_url = current_url
    headers = {
        "User-Agent": "IELTSTaskNewsMetadataBot/1.0 (+https://news.ieltstask.com)",
        "Accept": "text/html,application/xhtml+xml;q=0.9",
    }
    timeout = httpx.Timeout(settings.fetch_timeout_seconds)

    try:
        async with httpx.AsyncClient(headers=headers, timeout=timeout, follow_redirects=False) as client:
            for redirect_number in range(6):
                async with client.stream("GET", current_url) as response:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        location = response.headers.get("location")
                        if not location:
                            raise MetadataFetchError("The source returned an invalid redirect")
                        if redirect_number == 5:
                            raise MetadataFetchError("The source redirected too many times")
                        current_url = await ensure_public_url(urljoin(current_url, location))
                        continue

                    if response.status_code >= 400:
                        raise MetadataFetchError(f"The source returned HTTP {response.status_code}")

                    content_type = response.headers.get("content-type", "").lower()
                    if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                        raise MetadataFetchError("The URL did not return an HTML article")

                    content_length = response.headers.get("content-length")
                    if content_length and int(content_length) > settings.fetch_max_bytes:
                        raise MetadataFetchError("The article page is larger than the allowed limit")

                    chunks: list[bytes] = []
                    received = 0
                    async for chunk in response.aiter_bytes():
                        received += len(chunk)
                        if received > settings.fetch_max_bytes:
                            raise MetadataFetchError("The article page is larger than the allowed limit")
                        chunks.append(chunk)
                    encoding = response.encoding or "utf-8"
                    document = b"".join(chunks).decode(encoding, errors="replace")
                    final_url = current_url
                    break
            else:
                raise MetadataFetchError("The source could not be loaded")
    except MetadataFetchError:
        raise
    except (httpx.RequestError, UnicodeError, ValueError) as exc:
        raise MetadataFetchError("The source could not be fetched safely") from exc

    soup = BeautifulSoup(document, "html.parser")
    values = _metadata_map(soup)
    title = _clean_text(
        _first(values, "og:title", "twitter:title") or (soup.title.string if soup.title else None),
        500,
    )
    if not title:
        raise MetadataFetchError("No article title was found")

    description = _clean_text(
        _first(values, "og:description", "twitter:description", "description"),
        2_000,
    )
    author = _clean_text(_first(values, "author", "article:author", "parsely-author"), 300)
    source_name = _clean_text(_first(values, "og:site_name", "application-name"), 300)
    published_raw = _first(
        values,
        "article:published_time",
        "datepublished",
        "date",
        "parsely-pub-date",
    )

    canonical_tag = soup.find("link", rel=lambda rel: rel and "canonical" in rel)
    canonical_candidate = (
        str(canonical_tag.get("href")) if canonical_tag and canonical_tag.get("href") else final_url
    )
    try:
        canonical_url = await ensure_public_url(urljoin(final_url, canonical_candidate))
    except MetadataFetchError:
        canonical_url = final_url

    image_candidate = _first(values, "og:image:secure_url", "og:image", "twitter:image")
    image_url: str | None = None
    if image_candidate:
        try:
            safe_image_url = await ensure_public_url(urljoin(final_url, image_candidate))
            if urlsplit(safe_image_url).scheme == "https":
                image_url = safe_image_url
        except MetadataFetchError:
            image_url = None

    source_domain = (urlsplit(canonical_url).hostname or urlsplit(final_url).hostname or "unknown").lower()
    return ArticleMetadata(
        source_url=original_url,
        canonical_url=canonical_url,
        title=title,
        description=description,
        image_url=image_url,
        author=author,
        source_name=source_name,
        source_domain=source_domain,
        published_at=_parse_published_at(published_raw),
        raw_metadata={
            "og_type": _first(values, "og:type"),
            "published_raw": published_raw,
            "final_url": final_url,
        },
    )
