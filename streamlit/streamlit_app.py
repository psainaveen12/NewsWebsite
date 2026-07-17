from __future__ import annotations

import html
import os
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

import streamlit as st
from defusedxml import ElementTree


DEFAULT_SITE_URL = "https://news.ieltstask.com"
MAX_FEED_BYTES = 2 * 1024 * 1024


@dataclass(frozen=True)
class Story:
    title: str
    link: str
    summary: str
    published_at: datetime | None


def configured_site_url() -> str:
    value = os.getenv("NEWS_SITE_URL", "").strip()
    if not value:
        try:
            value = str(st.secrets.get("NEWS_SITE_URL", "")).strip()
        except (FileNotFoundError, KeyError):
            value = ""

    site_url = (value or DEFAULT_SITE_URL).rstrip("/")
    parsed = urlparse(site_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("NEWS_SITE_URL must be an absolute HTTP or HTTPS URL.")
    return site_url


def element_text(element: ElementTree.Element, tag: str) -> str:
    child = element.find(tag)
    return (child.text or "").strip() if child is not None else ""


@st.cache_data(ttl=300, show_spinner=False)
def load_feed(site_url: str) -> tuple[str, list[Story]]:
    request = Request(
        urljoin(f"{site_url}/", "feed.xml"),
        headers={"User-Agent": "IELTSTask-Streamlit/1.0 (+https://news.ieltstask.com)"},
    )
    with urlopen(request, timeout=10) as response:  # noqa: S310 - URL is operator configured.
        payload = response.read(MAX_FEED_BYTES + 1)
    if len(payload) > MAX_FEED_BYTES:
        raise ValueError("The RSS feed exceeds the 2 MB safety limit.")

    root = ElementTree.fromstring(payload)
    channel = root.find("channel")
    if channel is None:
        raise ValueError("The configured endpoint did not return a valid RSS channel.")

    feed_title = element_text(channel, "title") or "Latest News"
    stories: list[Story] = []
    for item in channel.findall("item"):
        title = element_text(item, "title") or "Untitled story"
        link = element_text(item, "link")
        if not link:
            continue

        published_at = None
        published = element_text(item, "pubDate")
        if published:
            try:
                published_at = parsedate_to_datetime(published)
            except (TypeError, ValueError):
                pass

        stories.append(
            Story(
                title=title,
                link=link,
                summary=element_text(item, "description"),
                published_at=published_at,
            )
        )
    return feed_title, stories


def story_date(story: Story) -> str:
    return story.published_at.strftime("%B %d, %Y") if story.published_at else "Latest update"


def story_card(story: Story, number: int) -> None:
    safe_title = html.escape(story.title)
    safe_summary = html.escape(story.summary or "Open the full article for the complete story.")
    safe_link = html.escape(story.link, quote=True)
    st.markdown(
        f"""
        <article class="story-card">
          <div class="story-number">{number:02d}</div>
          <div class="story-content">
            <div class="story-meta">LATEST NEWS <span></span> {story_date(story)}</div>
            <h2><a href="{safe_link}" target="_blank" rel="noopener noreferrer">{safe_title}</a></h2>
            <p>{safe_summary}</p>
            <a class="story-link" href="{safe_link}" target="_blank" rel="noopener noreferrer">Read full story <b>\u2197</b></a>
          </div>
        </article>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="Latest News | IELTS Task",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,600;6..72,700&display=swap');
    :root { --ink:#171716; --muted:#74736d; --paper:#fffdf7; --red:#e94723; --line:#dedbd1; --sun:#f4c34d; }
    .stApp { background:linear-gradient(145deg,#f4f0e6 0%,#fffdf7 48%,#eee7d8 100%); color:var(--ink); font-family:'DM Sans',sans-serif; }
    [data-testid="stHeader"] { background:transparent; }
    [data-testid="stToolbar"], #MainMenu, footer { display:none; }
    .block-container { max-width:1180px; padding-top:2.25rem; padding-bottom:4rem; }
    .masthead { display:flex; justify-content:space-between; align-items:center; padding:16px 0 19px; border-top:5px solid var(--ink); border-bottom:1px solid var(--ink); }
    .brand { display:flex; align-items:center; gap:13px; color:var(--ink); }
    .brand-mark { width:42px; height:42px; display:grid; place-items:center; background:var(--red); color:white; border-radius:50%; font:700 23px/1 'Newsreader',serif; transform:rotate(-7deg); }
    .brand-name { font:700 24px/1 'Newsreader',serif; letter-spacing:-.03em; }
    .brand-name small { display:block; margin-top:4px; color:var(--muted); font:600 9px/1 'DM Sans',sans-serif; letter-spacing:.2em; text-transform:uppercase; }
    .masthead-link { color:var(--ink)!important; font-size:12px; font-weight:700; letter-spacing:.12em; text-decoration:none!important; text-transform:uppercase; }
    .hero { display:grid; grid-template-columns:minmax(0,1.5fr) minmax(250px,.5fr); gap:40px; padding:70px 0 55px; border-bottom:1px solid var(--line); }
    .eyebrow { color:var(--red); font-size:11px; font-weight:700; letter-spacing:.2em; text-transform:uppercase; }
    .hero h1 { max-width:780px; margin:15px 0 18px; color:var(--ink); font:700 clamp(52px,7vw,94px)/.9 'Newsreader',serif; letter-spacing:-.055em; }
    .hero p { max-width:620px; margin:0; color:var(--muted); font-size:17px; line-height:1.65; }
    .hero-note { align-self:end; padding:24px; background:var(--sun); border:1px solid var(--ink); box-shadow:7px 7px 0 var(--ink); transform:rotate(1.5deg); }
    .hero-note b { display:block; margin-bottom:8px; font:700 23px/1.1 'Newsreader',serif; }
    .hero-note span { font-size:13px; line-height:1.5; }
    div[data-testid="stTextInput"] { max-width:560px; margin:32px 0 28px; }
    div[data-testid="stTextInput"] input { height:48px; border:1px solid var(--ink); border-radius:0; background:rgba(255,255,255,.7); color:var(--ink); box-shadow:4px 4px 0 var(--ink); }
    .section-bar { display:flex; justify-content:space-between; margin:20px 0 5px; padding-bottom:12px; border-bottom:3px solid var(--ink); color:var(--ink); font-size:11px; font-weight:700; letter-spacing:.17em; text-transform:uppercase; }
    .story-card { min-height:285px; display:grid; grid-template-columns:52px 1fr; gap:20px; padding:28px 4px 30px; border-bottom:1px solid var(--line); }
    .story-number { color:var(--red); font:600 20px/1 'Newsreader',serif; }
    .story-meta { color:var(--red); font-size:10px; font-weight:700; letter-spacing:.1em; }
    .story-meta span { display:inline-block; width:18px; height:1px; margin:0 7px 3px; background:var(--red); }
    .story-card h2 { margin:11px 0 10px; color:var(--ink); font:700 clamp(25px,3vw,37px)/1.04 'Newsreader',serif; letter-spacing:-.025em; }
    .story-card h2 a { color:inherit!important; text-decoration:none!important; }
    .story-card h2 a:hover { color:var(--red)!important; }
    .story-card p { display:-webkit-box; overflow:hidden; max-width:610px; margin:0 0 18px; color:var(--muted); font-size:14px; line-height:1.6; -webkit-box-orient:vertical; -webkit-line-clamp:3; }
    .story-link { color:var(--ink)!important; font-size:12px; font-weight:700; text-decoration:none!important; text-transform:uppercase; }
    .story-link b { color:var(--red); }
    .empty { margin:40px 0; padding:40px; border:1px solid var(--line); text-align:center; }
    @media (max-width:700px) {
      .block-container { padding-top:1rem; }
      .masthead { align-items:flex-start; }
      .brand-name { font-size:20px; }
      .masthead-link { display:none; }
      .hero { grid-template-columns:1fr; gap:28px; padding:45px 0 38px; }
      .hero h1 { font-size:54px; }
      .hero-note { max-width:320px; }
      .story-card { min-height:0; grid-template-columns:38px 1fr; gap:10px; padding-block:24px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

site_url = configured_site_url()
st.markdown(
    f"""
    <header class="masthead">
      <div class="brand"><div class="brand-mark">N</div><div class="brand-name">Latest News<small>IELTS Task Journal</small></div></div>
      <a class="masthead-link" href="{html.escape(site_url, quote=True)}" target="_blank" rel="noopener noreferrer">Open full website \u2197</a>
    </header>
    <section class="hero">
      <div><div class="eyebrow">Independent reporting and useful ideas</div><h1>Stories worth your attention.</h1><p>A focused reading desk for the newest reporting published by IELTS Task. Fresh stories are synchronized from the production news platform.</p></div>
      <div class="hero-note"><b>Live from the newsroom.</b><span>The feed refreshes automatically every five minutes. Article links open on the complete news website.</span></div>
    </section>
    """,
    unsafe_allow_html=True,
)

try:
    feed_title, all_stories = load_feed(site_url)
except Exception as exc:  # Streamlit should remain useful when the origin is temporarily offline.
    st.error(f"The production news feed is unavailable: {exc}")
    st.info("Start the Docker application or set NEWS_SITE_URL in Streamlit secrets to a reachable deployment URL.")
    st.link_button("Open production website", site_url)
    st.stop()

query = st.text_input("Search the latest stories", placeholder="Search headlines and descriptions...").strip().casefold()
stories = [story for story in all_stories if query in f"{story.title} {story.summary}".casefold()] if query else all_stories

st.markdown(
    f'<div class="section-bar"><span>{html.escape(feed_title)}</span><span>{len(stories)} stories</span></div>',
    unsafe_allow_html=True,
)

if not stories:
    st.markdown('<div class="empty"><b>No matching stories.</b><br>Try a broader search phrase.</div>', unsafe_allow_html=True)
else:
    left, right = st.columns(2, gap="large")
    for index, story in enumerate(stories, start=1):
        with left if index % 2 else right:
            story_card(story, index)

