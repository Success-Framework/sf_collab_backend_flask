import logging
import hashlib
from datetime import datetime
from email.utils import parsedate_to_datetime

import requests
import feedparser
from bs4 import BeautifulSoup

from app.extensions import db
from app.models.aiNews import AINewsArticle
from .sources import get_active_sources

logger = logging.getLogger(__name__)

# ── HTTP request headers to avoid blocks ─────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; SFCollabBot/1.0; +https://sfcollab.com)"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

REQUEST_TIMEOUT = 15  # seconds


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_date(date_str):
    """
    Try to parse a date string from RSS into a Python datetime.
    Returns None if unparseable so we don't crash on bad feeds.
    """
    if not date_str:
        return None
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        pass
    # Fallback: common ISO format
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def _truncate(text, max_len=500):
    """Truncate text to max_len characters cleanly."""
    if not text:
        return None
    text = text.strip()
    return text if len(text) <= max_len else text[:max_len].rsplit(" ", 1)[0] + "…"


def _extract_image(entry):
    """
    Try to pull an image URL from an RSS entry.
    Checks media:content, media:thumbnail, and summary HTML.
    """
    # media:content
    media_content = getattr(entry, "media_content", None)
    if media_content and isinstance(media_content, list):
        for m in media_content:
            url = m.get("url", "")
            if url and any(url.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp")):
                return url

    # media:thumbnail
    media_thumb = getattr(entry, "media_thumbnail", None)
    if media_thumb and isinstance(media_thumb, list):
        url = media_thumb[0].get("url", "")
        if url:
            return url

    # Parse first <img> from summary/content HTML
    html = (
        getattr(entry, "summary", "")
        or (entry.get("content", [{}])[0].get("value", "") if entry.get("content") else "")
    )
    if html:
        soup = BeautifulSoup(html, "html.parser")
        img = soup.find("img")
        if img and img.get("src"):
            return img["src"]

    return None


def _clean_summary(entry):
    """
    Strip HTML tags from the RSS summary/description and truncate.
    """
    raw = (
        getattr(entry, "summary", "")
        or (entry.get("content", [{}])[0].get("value", "") if entry.get("content") else "")
    )
    if not raw:
        return None
    text = BeautifulSoup(raw, "html.parser").get_text(separator=" ")
    return _truncate(text, 500)


def _build_tags(entry, source_key, category):
    """
    Build a comma-separated tag string from entry categories + source key.
    """
    tags = set()
    tags.add(source_key)
    tags.add(category.lower().replace(" ", "_"))

    for tag in getattr(entry, "tags", []):
        term = tag.get("term", "").strip().lower()
        if term and len(term) < 50:
            tags.add(term)

    return ",".join(sorted(tags))


def _article_exists(url):
    """Check if an article with this URL is already in the DB."""
    return db.session.query(
        AINewsArticle.query.filter_by(url=url).exists()
    ).scalar()


# ── RSS Scraper ───────────────────────────────────────────────────────────────

def _scrape_rss(source):
    """
    Parse an RSS/Atom feed and return a list of AINewsArticle objects
    (not yet committed to DB).
    """
    key = source["key"]
    label = source["label"]
    feed_url = source["url"]
    category = source["category"]
    impact = source["impact"]

    articles = []

    try:
        response = requests.get(feed_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.warning(f"[{key}] Failed to fetch feed: {e}")
        return articles

    feed = feedparser.parse(response.content)

    if feed.bozo and not feed.entries:
        logger.warning(f"[{key}] Feed parse error: {feed.bozo_exception}")
        return articles

    logger.info(f"[{key}] Fetched {len(feed.entries)} entries from {label}")

    for entry in feed.entries[:source.get("max_articles", 20)]:
        url = getattr(entry, "link", "").strip()
        title = getattr(entry, "title", "").strip()

        # Skip if missing essentials
        if not url or not title:
            continue

        # Skip duplicates already in DB
        if _article_exists(url):
            continue

        article = AINewsArticle(
            title=title,
            url=url,
            summary=_clean_summary(entry),
            author=getattr(entry, "author", None),
            image_url=_extract_image(entry),
            source=key,
            source_label=label,
            category=category,
            tags=_build_tags(entry, key, category),
            impact_score=impact,
            published_at=_parse_date(getattr(entry, "published", None)),
            scraped_at=datetime.utcnow(),
        )
        articles.append(article)

    return articles


# ── HTML Fallback Scraper ─────────────────────────────────────────────────────

def _scrape_html(source):
    """
    Fallback HTML scraper for sources without RSS.
    Looks for <article> or <a> tags with title-like text.
    This is best-effort — RSS is always preferred.
    """
    key = source["key"]
    label = source["label"]
    page_url = source["url"]
    category = source["category"]
    impact = source["impact"]

    articles = []

    try:
        response = requests.get(page_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.warning(f"[{key}] HTML fetch failed: {e}")
        return articles

    soup = BeautifulSoup(response.text, "html.parser")

    # Try <article> blocks first, then fallback to <a> tags
    blocks = soup.find_all("article") or soup.find_all("a", href=True)

    seen_urls = set()

    for block in blocks[:20]:  # cap at 20 per source
        # Get link
        link_tag = block if block.name == "a" else block.find("a", href=True)
        if not link_tag:
            continue

        url = link_tag.get("href", "").strip()
        if not url.startswith("http"):
            # Make relative URLs absolute
            from urllib.parse import urljoin
            url = urljoin(page_url, url)

        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        # Get title
        title_tag = block.find(["h1", "h2", "h3"]) or link_tag
        title = title_tag.get_text(strip=True) if title_tag else ""

        if not title or len(title) < 10:
            continue

        if _article_exists(url):
            continue

        article = AINewsArticle(
            title=title[:500],
            url=url,
            summary=None,
            author=None,
            image_url=None,
            source=key,
            source_label=label,
            category=category,
            tags=f"{key},{category.lower().replace(' ', '_')}",
            impact_score=impact,
            published_at=None,
            scraped_at=datetime.utcnow(),
        )
        articles.append(article)

    return articles


# ── Main Entry Point ──────────────────────────────────────────────────────────

def run_scraper(source_keys=None):
    """
    Main scraper function. Call this to scrape all (or specific) sources.

    Args:
        source_keys (list, optional): List of source keys to scrape.
                                      If None, scrapes all active sources.

    Returns:
        dict: Summary of results per source.
    """
    sources = get_active_sources()

    # Filter to specific keys if provided
    if source_keys:
        sources = [s for s in sources if s["key"] in source_keys]

    results = {
        "total_saved": 0,
        "total_skipped": 0,
        "sources": {}
    }

    for source in sources:
        key = source["key"]
        scrape_fn = _scrape_rss if source["type"] == "rss" else _scrape_html

        try:
            articles = scrape_fn(source)
            saved = 0

            for article in articles:
                try:
                    db.session.add(article)
                    db.session.commit()
                    saved += 1
                except Exception as e:
                    db.session.rollback()
                    # Most likely a duplicate URL race condition — safe to skip
                    logger.debug(f"[{key}] Skipped article (likely duplicate): {e}")

            skipped = len(articles) - saved
            results["sources"][key] = {
                "fetched": len(articles),
                "saved": saved,
                "skipped": skipped,
                "status": "ok"
            }
            results["total_saved"] += saved
            results["total_skipped"] += skipped
            logger.info(f"[{key}] Done — saved {saved}, skipped {skipped}")

        except Exception as e:
            logger.error(f"[{key}] Scraper crashed: {e}")
            results["sources"][key] = {
                "fetched": 0,
                "saved": 0,
                "skipped": 0,
                "status": f"error: {str(e)}"
            }

    return results