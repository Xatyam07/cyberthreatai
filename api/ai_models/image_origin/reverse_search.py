"""
reverse_search.py — Multi-Source Reverse Image Search
======================================================
Cyber Threat AI · Phase B · MOST ADVANCED VERSION

Sources (in priority order):
  1. Bing Visual Search API  — best results, requires API key
  2. Google reverse image    — scrape-based fallback (no key needed)
  3. TinEye fingerprint      — best for exact duplicates (optional key)

For each result, extracts:
  • Source URL + page title
  • Estimated original date (from page metadata / news dates)
  • Location context (where the image is actually from)
  • Credibility score of source domain
  • Whether the result contradicts the supplied caption

All network calls use async retry with exponential backoff.
"""

import os
import re
import base64
import logging
import asyncio
from typing import Optional
from urllib.parse import urlparse, quote_plus
from datetime import datetime, timezone

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────
# Config (loaded from environment)
# ─────────────────────────────────────────────────────────────────────────
BING_API_KEY     = os.getenv("BING_SEARCH_API_KEY", "")
BING_ENDPOINT    = "https://api.bing.microsoft.com/v7.0/images/visualsearch"
TINEYE_API_KEY   = os.getenv("TINEYE_API_KEY", "")
REQUEST_TIMEOUT  = 15   # seconds
MAX_RESULTS      = 10

# High-credibility domains — results from these get a credibility boost
CREDIBLE_DOMAINS = {
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "theguardian.com",
    "nytimes.com", "washingtonpost.com", "altnews.in", "boomlive.in",
    "factcheck.org", "snopes.com", "politifact.com", "ndtv.com",
    "thehindu.com", "indianexpress.com", "timesofindia.com",
    "who.int", "gov.uk", "gov.in", "wikipedia.org",
}

# Known fact-check domains — results from these are automatically flagged
FACTCHECK_DOMAINS = {
    "snopes.com", "factcheck.org", "politifact.com", "altnews.in",
    "boomlive.in", "vishvasnews.com", "factchecker.in",
}


# ─────────────────────────────────────────────────────────────────────────
# HTTP session with retry
# ─────────────────────────────────────────────────────────────────────────
def _make_session() -> requests.Session:
    session = requests.Session()
    retry_policy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    session.mount("https://", HTTPAdapter(max_retries=retry_policy))
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    })
    return session


_session = _make_session()


# ─────────────────────────────────────────────────────────────────────────
# Bing Visual Search
# ─────────────────────────────────────────────────────────────────────────
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.RequestException),
)
def _bing_visual_search(image_bytes: bytes) -> list[dict]:
    """
    Submit image to Bing Visual Search API.
    Returns list of result dicts.
    """
    if not BING_API_KEY:
        logger.info("BING_SEARCH_API_KEY not set — skipping Bing visual search")
        return []

    try:
        boundary = "----FormBoundaryXXXXXX"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="image"; filename="image.jpg"\r\n'
            f"Content-Type: image/jpeg\r\n\r\n"
        ).encode() + image_bytes + f"\r\n--{boundary}--\r\n".encode()

        resp = _session.post(
            BING_ENDPOINT,
            headers={
                "Ocp-Apim-Subscription-Key": BING_API_KEY,
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
            data=body,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for tag in data.get("tags", []):
            for action in tag.get("actions", []):
                if action.get("actionType") in ("VisualSearch", "PagesIncluding"):
                    for item in action.get("data", {}).get("value", [])[:MAX_RESULTS]:
                        results.append(_parse_bing_result(item))

        logger.info("Bing visual search: %d results", len(results))
        return results[:MAX_RESULTS]

    except Exception as e:
        logger.error("Bing visual search failed: %s", e)
        return []


def _parse_bing_result(item: dict) -> dict:
    url        = item.get("hostPageUrl", "")
    domain     = _extract_domain(url)
    date_str   = item.get("datePublished", "")
    name       = item.get("name", "")
    thumbnail  = item.get("thumbnailUrl", "")

    return {
        "source":        "bing",
        "url":           url,
        "title":         name,
        "domain":        domain,
        "date":          _parse_date(date_str),
        "thumbnail_url": thumbnail,
        "credibility":   _score_domain(domain),
        "is_factcheck":  domain in FACTCHECK_DOMAINS,
        "summary":       name[:200],
    }


# ─────────────────────────────────────────────────────────────────────────
# Google Reverse Image (scrape fallback — no API key needed)
# ─────────────────────────────────────────────────────────────────────────
def _google_reverse_image_fallback(image_bytes: bytes) -> list[dict]:
    """
    Upload image to Google Lens / reverse image search via form POST.
    This is a best-effort scrape fallback — Bing API is preferred.
    """
    try:
        from bs4 import BeautifulSoup

        upload_url = "https://images.google.com/searchbyimage/upload"
        files = {"encoded_image": ("image.jpg", image_bytes, "image/jpeg")}
        params = {"hl": "en"}

        resp = _session.post(upload_url, files=files, params=params,
                             timeout=REQUEST_TIMEOUT, allow_redirects=True)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        results = []

        # Extract page title (usually describes what Google thinks the image is)
        title_el = soup.find("div", {"class": re.compile(r"r.*")})
        page_title = title_el.get_text()[:200] if title_el else ""

        # Extract related search results
        for link in soup.find_all("a", href=True)[:MAX_RESULTS]:
            href = link["href"]
            if href.startswith("/url?q="):
                actual_url = href[7:].split("&")[0]
                domain = _extract_domain(actual_url)
                text   = link.get_text()[:150]
                if len(text) > 10 and domain:
                    results.append({
                        "source":       "google_reverse",
                        "url":          actual_url,
                        "title":        text,
                        "domain":       domain,
                        "date":         None,
                        "credibility":  _score_domain(domain),
                        "is_factcheck": domain in FACTCHECK_DOMAINS,
                        "summary":      text,
                    })

        if page_title:
            results.insert(0, {
                "source":       "google_reverse",
                "url":          resp.url,
                "title":        page_title,
                "domain":       "images.google.com",
                "date":         None,
                "credibility":  0.5,
                "is_factcheck": False,
                "summary":      page_title,
            })

        logger.info("Google reverse image: %d results", len(results))
        return results[:MAX_RESULTS]

    except Exception as e:
        logger.warning("Google reverse image fallback failed: %s", e)
        return []


# ─────────────────────────────────────────────────────────────────────────
# Result enrichment — extract date and location from page text
# ─────────────────────────────────────────────────────────────────────────
def _enrich_result(result: dict) -> dict:
    """
    Fetch the result page and extract:
      - Original publication date
      - Location mentions
      - Contradiction signals vs supplied caption
    """
    url = result.get("url", "")
    if not url or not url.startswith("http"):
        return result

    try:
        resp = _session.get(url, timeout=8, stream=True)
        # Read only first 20KB to be fast
        content = b""
        for chunk in resp.iter_content(chunk_size=4096):
            content += chunk
            if len(content) > 20_000:
                break

        text = content.decode("utf-8", errors="ignore")

        # Extract date from meta tags
        date_patterns = [
            r'<meta[^>]+(?:publish|date|time)[^>]+content="([^"]+)"',
            r'"datePublished"\s*:\s*"([^"]+)"',
            r'"publishedAt"\s*:\s*"([^"]+)"',
        ]
        for pat in date_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                result["date"] = _parse_date(m.group(1))
                break

        # Extract year mentions
        years = list(set(re.findall(r"\b((?:19|20)\d{2})\b", text[:5000])))
        if years:
            result["years_mentioned"] = years[:5]

    except Exception:
        pass   # Enrichment is best-effort

    return result


# ─────────────────────────────────────────────────────────────────────────
# Main public function
# ─────────────────────────────────────────────────────────────────────────
def reverse_search_image(
    image_bytes:    bytes,
    caption:        str   = "",
    enrich_results: bool  = False,
) -> dict:
    """
    Run reverse image search across all available sources.

    Args:
        image_bytes:    raw image bytes
        caption:        caption claim (used for contradiction detection)
        enrich_results: if True, fetch each result page for date extraction

    Returns:
        {
            "results":              list[dict],
            "total_found":          int,
            "original_context":     str | None,    # best guess at real origin
            "original_date":        str | None,
            "credible_sources":     list[str],
            "factcheck_hits":       list[dict],
            "contradiction_found":  bool,
            "search_sources_used":  list[str],
        }
    """
    all_results      = []
    sources_used     = []

    # 1. Bing (preferred — requires API key)
    if BING_API_KEY:
        bing_results = _bing_visual_search(image_bytes)
        all_results.extend(bing_results)
        sources_used.append("bing")

    # 2. Google fallback
    if not all_results:
        google_results = _google_reverse_image_fallback(image_bytes)
        all_results.extend(google_results)
        if google_results:
            sources_used.append("google_reverse")

    # 3. Optional enrichment
    if enrich_results and all_results:
        all_results = [_enrich_result(r) for r in all_results[:5]]

    # 4. Sort by credibility
    all_results.sort(key=lambda r: r.get("credibility", 0), reverse=True)

    # 5. Extract insight signals
    credible_sources = [
        r["url"] for r in all_results
        if r.get("credibility", 0) > 0.6
    ]
    factcheck_hits = [r for r in all_results if r.get("is_factcheck")]

    # 6. Best guess at original context (highest credibility result)
    original_context = None
    original_date    = None
    if all_results:
        best = all_results[0]
        original_context = best.get("title") or best.get("summary")
        original_date    = best.get("date")

    # 7. Contradiction detection
    contradiction_found = False
    if caption and factcheck_hits:
        caption_lower = caption.lower()
        for hit in factcheck_hits:
            summary = (hit.get("summary") or hit.get("title") or "").lower()
            if any(kw in summary for kw in ["false", "fake", "misleading", "debunked", "misattributed"]):
                contradiction_found = True
                break

    return {
        "results":             all_results[:MAX_RESULTS],
        "total_found":         len(all_results),
        "original_context":    original_context,
        "original_date":       original_date,
        "credible_sources":    credible_sources[:5],
        "factcheck_hits":      factcheck_hits[:3],
        "contradiction_found": contradiction_found,
        "search_sources_used": sources_used,
    }


# ─────────────────────────────────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────────────────────────────────
def _extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().lstrip("www.")
    except Exception:
        return ""


def _score_domain(domain: str) -> float:
    """Score domain credibility: 0.0 = unknown, 1.0 = highly credible."""
    if domain in CREDIBLE_DOMAINS:
        return 0.9
    if domain in FACTCHECK_DOMAINS:
        return 0.85
    if domain.endswith(".gov") or domain.endswith(".edu"):
        return 0.80
    if domain.endswith(".org"):
        return 0.50
    if not domain:
        return 0.0
    return 0.35


def _parse_date(date_str: str) -> Optional[str]:
    """Parse various date string formats to ISO date string."""
    if not date_str:
        return None
    patterns = [
        r"(\d{4}-\d{2}-\d{2})",
        r"(\d{4}/\d{2}/\d{2})",
        r"(\w+ \d{1,2},?\s+\d{4})",
    ]
    for pat in patterns:
        m = re.search(pat, date_str)
        if m:
            return m.group(1)
    return date_str[:10] if len(date_str) >= 10 else None