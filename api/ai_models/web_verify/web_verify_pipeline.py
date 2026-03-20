"""
web_verify/ — Web Verification Pipeline
========================================
Cyber Threat AI · Phase D · MOST ADVANCED VERSION

Three modules in one file for clean delivery:

  news_searcher.py    — Google News + NewsAPI + RSS feeds
  factcheck_lookup.py — Snopes / AltNews / FactCheck.org scraping
  evidence_scorer.py  — NLI-based evidence-to-claim scoring

Together they answer: "Does the open web support or contradict this claim?"

Evidence scoring uses facebook/bart-large-mnli (same model as zero-shot)
in NLI mode: for each (claim, evidence) pair, classify as
ENTAILMENT / NEUTRAL / CONTRADICTION and aggregate.
"""

import os
import re
import logging
import hashlib
from typing import Optional
from urllib.parse import quote_plus, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────
NEWS_API_KEY     = os.getenv("NEWS_API_KEY", "")
BING_NEWS_KEY    = os.getenv("BING_SEARCH_API_KEY", "")
REQUEST_TIMEOUT  = 12
MAX_EVIDENCE     = 8

# NLI thresholds
CONTRADICTION_MIN  = 0.45
ENTAILMENT_MIN     = 0.45


# ─────────────────────────────────────────────────────────────────────────
# HTTP session
# ─────────────────────────────────────────────────────────────────────────
def _session() -> requests.Session:
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504])))
    s.headers["User-Agent"] = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36")
    return s


_http = _session()


# ═══════════════════════════════════════════════════════════════════════════
# NEWS SEARCHER
# ═══════════════════════════════════════════════════════════════════════════

@retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=5))
def _newsapi_search(query: str) -> list[dict]:
    """NewsAPI.org — requires free API key."""
    if not NEWS_API_KEY:
        return []
    try:
        resp = _http.get(
            "https://newsapi.org/v2/everything",
            params={
                "q":          query[:100],
                "sortBy":     "relevancy",
                "pageSize":   MAX_EVIDENCE,
                "language":   "en",
                "apiKey":     NEWS_API_KEY,
            },
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        return [
            {
                "title":       a.get("title", ""),
                "description": a.get("description", ""),
                "url":         a.get("url", ""),
                "source":      a.get("source", {}).get("name", ""),
                "published":   a.get("publishedAt", ""),
                "summary":     f"{a.get('title','')} — {a.get('description','')}",
            }
            for a in articles
        ]
    except Exception as e:
        logger.warning("NewsAPI search failed: %s", e)
        return []


def _bing_news_search(query: str) -> list[dict]:
    """Bing News Search API."""
    if not BING_NEWS_KEY:
        return []
    try:
        resp = _http.get(
            "https://api.bing.microsoft.com/v7.0/news/search",
            headers={"Ocp-Apim-Subscription-Key": BING_NEWS_KEY},
            params={"q": query[:100], "count": MAX_EVIDENCE, "mkt": "en-IN"},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        return [
            {
                "title":    a.get("name", ""),
                "url":      a.get("url", ""),
                "source":   a.get("provider", [{}])[0].get("name", ""),
                "published":a.get("datePublished", ""),
                "summary":  a.get("description", ""),
            }
            for a in resp.json().get("value", [])
        ]
    except Exception as e:
        logger.warning("Bing news search failed: %s", e)
        return []


def _google_news_rss(query: str) -> list[dict]:
    """Google News RSS — no API key needed."""
    try:
        from bs4 import BeautifulSoup
        url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-IN&gl=IN&ceid=IN:en"
        resp = _http.get(url, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(resp.content, "xml")

        results = []
        for item in soup.find_all("item")[:MAX_EVIDENCE]:
            title = item.find("title")
            link  = item.find("link")
            desc  = item.find("description")
            pub   = item.find("pubDate")
            src   = item.find("source")
            results.append({
                "title":    title.text if title else "",
                "url":      link.text if link else "",
                "source":   src.text if src else "Google News",
                "published":pub.text if pub else "",
                "summary":  (desc.text if desc else "")[:200],
            })
        logger.info("Google News RSS: %d articles for query '%s'", len(results), query[:40])
        return results
    except Exception as e:
        logger.warning("Google News RSS failed: %s", e)
        return []


def search_news(query: str) -> list[str]:
    """
    Search multiple news sources and return list of summary strings.
    Used by /verify endpoint as evidence input.
    """
    all_results = []

    # Priority: Bing News → NewsAPI → Google RSS
    all_results.extend(_bing_news_search(query))
    if len(all_results) < 3:
        all_results.extend(_newsapi_search(query))
    if len(all_results) < 3:
        all_results.extend(_google_news_rss(query))

    # Deduplicate by title hash
    seen    = set()
    unique  = []
    for r in all_results:
        h = hashlib.md5(r.get("title", "").encode()).hexdigest()
        if h not in seen:
            seen.add(h)
            unique.append(r)

    # Return summary strings for consumption by contradiction_scorer
    return [
        f"{r.get('source','')}: {r.get('title','')} — {r.get('summary','')}"
        for r in unique[:MAX_EVIDENCE]
    ]


# ═══════════════════════════════════════════════════════════════════════════
# FACTCHECK LOOKUP
# ═══════════════════════════════════════════════════════════════════════════

_FACTCHECK_SOURCES = [
    {
        "name":    "AltNews",
        "search":  "https://www.altnews.in/?s={}",
        "domain":  "altnews.in",
    },
    {
        "name":    "BoomLive",
        "search":  "https://www.boomlive.in/search?query={}",
        "domain":  "boomlive.in",
    },
    {
        "name":    "Snopes",
        "search":  "https://www.snopes.com/?s={}",
        "domain":  "snopes.com",
    },
    {
        "name":    "FactCheck.org",
        "search":  "https://www.factcheck.org/?s={}",
        "domain":  "factcheck.org",
    },
]

_VERDICT_PATTERNS = {
    "false":        ["false", "fake", "debunked", "no evidence", "misleading", "incorrect"],
    "true":         ["true", "accurate", "correct", "verified", "confirmed"],
    "mixed":        ["mixed", "partly true", "partly false", "needs context", "misleading"],
    "unverifiable": ["unverifiable", "outdated", "satire", "opinion"],
}


def lookup_factchecks(claim: str) -> list[str]:
    """
    Search fact-check sites for verdicts on the claim.
    Returns list of summary strings.
    """
    results   = []
    query_enc = quote_plus(claim[:120])

    for source in _FACTCHECK_SOURCES:
        try:
            from bs4 import BeautifulSoup
            url  = source["search"].format(query_enc)
            resp = _http.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                continue

            soup  = BeautifulSoup(resp.text, "lxml")
            links = soup.find_all("a", href=True)

            for a in links[:5]:
                href  = a.get("href", "")
                text  = a.get_text(strip=True)
                if (source["domain"] in href and len(text) > 20
                        and any(kw in text.lower() for kw in
                                ["false", "fake", "true", "fact", "mislead", "claim", "debunk"])):
                    verdict = _extract_verdict(text)
                    results.append(
                        f"[{source['name']}] {verdict.upper()}: {text[:160]} — {href}"
                    )
                    break

        except Exception as e:
            logger.debug("Factcheck lookup failed for %s: %s", source["name"], e)

    return results[:MAX_EVIDENCE]


def _extract_verdict(text: str) -> str:
    text_lower = text.lower()
    for verdict, patterns in _VERDICT_PATTERNS.items():
        if any(p in text_lower for p in patterns):
            return verdict
    return "unverified"


# ═══════════════════════════════════════════════════════════════════════════
# EVIDENCE SCORER — NLI-based claim vs evidence scoring
# ═══════════════════════════════════════════════════════════════════════════

_nli_pipeline = None


def _get_nli_pipeline():
    """Lazy-load NLI pipeline (reuses bart-large-mnli from text engine)."""
    global _nli_pipeline
    if _nli_pipeline is None:
        try:
            from transformers import pipeline
            _nli_pipeline = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1,
            )
            logger.info("NLI pipeline loaded for evidence scoring")
        except Exception as e:
            logger.warning("NLI pipeline unavailable: %s", e)
    return _nli_pipeline


def score_evidence(claim: str, evidence_list: list[str]) -> dict:
    """
    Score each evidence string against the claim using NLI.

    For each (claim, evidence) pair:
      ENTAILMENT   → evidence supports the claim
      NEUTRAL      → evidence is unrelated
      CONTRADICTION → evidence contradicts the claim

    Returns:
        {
            "overall_verdict":      "SUPPORTED" | "CONTRADICTED" | "INSUFFICIENT",
            "support_score":        float,      # 0–1
            "contradiction_score":  float,      # 0–1
            "evidence_count":       int,
            "supporting":           list[str],
            "contradicting":        list[str],
            "scored_evidence":      list[dict],
        }
    """
    if not evidence_list:
        return {
            "overall_verdict":     "INSUFFICIENT",
            "support_score":       0.0,
            "contradiction_score": 0.0,
            "evidence_count":      0,
            "supporting":          [],
            "contradicting":       [],
            "scored_evidence":     [],
        }

    pipe = _get_nli_pipeline()
    if pipe is None:
        # Fallback: keyword-based scoring
        return _keyword_evidence_score(claim, evidence_list)

    scored     = []
    supporting = []
    contradicting = []

    for ev in evidence_list[:MAX_EVIDENCE]:
        # Truncate for model input
        premise    = ev[:400]
        hypothesis = claim[:200]

        try:
            result = pipe(
                premise,
                candidate_labels=["entailment", "neutral", "contradiction"],
                hypothesis_template="{}",
            )
            label_scores = dict(zip(result["labels"], result["scores"]))

            ent  = label_scores.get("entailment", 0)
            cont = label_scores.get("contradiction", 0)
            neut = label_scores.get("neutral", 0)

            nli_verdict = "neutral"
            if ent > ENTAILMENT_MIN and ent > cont:
                nli_verdict  = "entailment"
                supporting.append(ev[:120])
            elif cont > CONTRADICTION_MIN and cont > ent:
                nli_verdict  = "contradiction"
                contradicting.append(ev[:120])

            scored.append({
                "evidence":    ev[:120],
                "verdict":     nli_verdict,
                "entailment":  round(ent, 3),
                "contradiction": round(cont, 3),
                "neutral":     round(neut, 3),
            })
        except Exception as e:
            logger.debug("NLI scoring failed for evidence: %s", e)

    # Aggregate scores
    n = len(scored)
    if n == 0:
        support_score = 0.0
        contra_score  = 0.0
    else:
        support_score = len(supporting) / n
        contra_score  = len(contradicting) / n

    if contra_score >= 0.4:
        overall = "CONTRADICTED"
    elif support_score >= 0.4:
        overall = "SUPPORTED"
    else:
        overall = "INSUFFICIENT"

    return {
        "overall_verdict":     overall,
        "support_score":       round(support_score, 4),
        "contradiction_score": round(contra_score, 4),
        "evidence_count":      n,
        "supporting":          supporting[:3],
        "contradicting":       contradicting[:3],
        "scored_evidence":     scored,
    }


def _keyword_evidence_score(claim: str, evidence_list: list[str]) -> dict:
    """Fallback keyword-based scoring when NLI model unavailable."""
    claim_lower = claim.lower()
    supporting  = []
    contradicting = []

    for ev in evidence_list:
        ev_lower = ev.lower()
        if any(w in ev_lower for w in ["false", "fake", "misleading", "debunked", "not true"]):
            contradicting.append(ev[:120])
        elif any(w in ev_lower for w in ["confirmed", "true", "verified", "accurate"]):
            supporting.append(ev[:120])

    n = len(evidence_list)
    return {
        "overall_verdict":     "CONTRADICTED" if contradicting else ("SUPPORTED" if supporting else "INSUFFICIENT"),
        "support_score":       round(len(supporting) / max(n, 1), 4),
        "contradiction_score": round(len(contradicting) / max(n, 1), 4),
        "evidence_count":      n,
        "supporting":          supporting[:3],
        "contradicting":       contradicting[:3],
        "scored_evidence":     [],
    }