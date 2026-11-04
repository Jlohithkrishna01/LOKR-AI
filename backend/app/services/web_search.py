# ============================================================================
# LOKR AI - Multi-Engine Resilient Web Grounding & Search Service
# ============================================================================

import re
import time
import threading
import logging
import urllib.parse
from html.parser import HTMLParser
from typing import Optional, List, Dict
from urllib.parse import urlparse

import httpx
from ddgs import DDGS

from app.services.grounding_service import (
    classify_query_intent,
    rank_and_deduplicate_sources,
)

logger = logging.getLogger("lumiq.web_search")

# User-Agent for resilient external HTTP search requests
STANDARD_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
WIKIPEDIA_USER_AGENT = "LOKR-AI/1.0 (https://lokr.ai; contact@lokr.ai)"

# Thread-safe in-memory cache
_SEARCH_CACHE: Dict[str, Dict] = {}
_CACHE_LOCK = threading.Lock()

class _DDGHTMLParser(HTMLParser):
    """Zero-dependency HTML parser for DuckDuckGo HTML search results."""
    def __init__(self):
        super().__init__()
        self.results: List[Dict[str, str]] = []
        self._current_result: Optional[Dict[str, str]] = None
        self._in_a = False
        self._in_snippet = False
        self._buffer: List[str] = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        c = attrs_dict.get("class", "")
        if tag == "div" and "result " in f"{c} ":
            self._current_result = {"title": "", "url": "", "snippet": "", "source_name": ""}
        elif tag == "a" and "result__a" in c and self._current_result is not None:
            self._in_a = True
            href = attrs_dict.get("href", "")
            if "uddg=" in href:
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                clean_url = parsed.get("uddg", [href])[0]
            else:
                clean_url = href
            self._current_result["url"] = clean_url
            self._current_result["source_name"] = extract_source_name(clean_url)
            self._buffer = []
        elif tag == "a" and "result__snippet" in c and self._current_result is not None:
            self._in_snippet = True
            self._buffer = []

    def handle_endtag(self, tag):
        if tag == "a":
            text = "".join(self._buffer).strip()
            if self._in_a and self._current_result is not None:
                self._current_result["title"] = text
                self._in_a = False
            elif self._in_snippet and self._current_result is not None:
                self._current_result["snippet"] = text
                self._in_snippet = False
            self._buffer = []
        elif tag == "div" and self._current_result is not None:
            if self._current_result.get("url") and self._current_result["url"].startswith("http"):
                self.results.append(self._current_result)
            self._current_result = None

    def handle_data(self, data):
        if self._in_a or self._in_snippet:
            self._buffer.append(data)

def extract_source_name(url: str) -> str:
    """Extracts clean, readable source label from URL domain."""
    try:
        domain = urlparse(url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        parts = domain.split(".")
        if len(parts) >= 2:
            return parts[0].capitalize()
        return domain
    except Exception:
        return "Web Source"

def should_search_web(query: str, explicit_flag: Optional[bool] = None, client_timezone: str = "Asia/Kolkata") -> bool:
    """
    Decides whether web search is required based on the decision layer.
    Respects explicit user toggles and filters out pure date/time queries and stable general knowledge.
    """
    if explicit_flag is not None:
        return explicit_flag

    decision = classify_query_intent(query, client_timezone=client_timezone)
    return decision.should_search

def _search_ddgs_multi(query: str, max_results: int = 6) -> List[Dict[str, str]]:
    """Engine 1: Multi-provider search via DDGS."""
    results = []
    seen_urls = set()
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results + 3))
            for item in raw_results:
                url = item.get("href") or item.get("url") or ""
                if not url or url in seen_urls or not url.startswith("http"):
                    continue
                seen_urls.add(url)
                title = (item.get("title") or "Untitled Source").strip()
                snippet = (item.get("body") or item.get("snippet") or "").strip()
                if snippet:
                    results.append({
                        "title": title,
                        "url": url,
                        "source_name": extract_source_name(url),
                        "snippet": snippet
                    })
                if len(results) >= max_results:
                    break
    except Exception as e:
        logger.debug(f"[DDGS Multi] Primary text search error: {e}")
    return results

def _search_ddg_html(query: str, max_results: int = 6) -> List[Dict[str, str]]:
    """Engine 2: Direct DuckDuckGo HTML endpoint fallback."""
    headers = {
        "User-Agent": STANDARD_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    url = "https://html.duckduckgo.com/html/"
    try:
        with httpx.Client(timeout=8.0, follow_redirects=True, headers=headers) as client:
            resp = client.post(url, data={"q": query})
            if resp.status_code == 200:
                parser = _DDGHTMLParser()
                parser.feed(resp.text)
                return parser.results[:max_results]
    except Exception as e:
        logger.debug(f"[DDG HTML] Fallback search error: {e}")
    return []

def _search_wikipedia_api(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """Engine 3: Wikipedia Knowledge API fallback for encyclopedic entities."""
    headers = {"User-Agent": WIKIPEDIA_USER_AGENT}
    endpoint = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "utf8": "1",
        "format": "json",
        "srlimit": max_results
    }
    results = []
    try:
        with httpx.Client(timeout=6.0, headers=headers) as client:
            resp = client.get(endpoint, params=params)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("query", {}).get("search", [])
                for item in items:
                    title = item.get("title", "")
                    raw_snippet = item.get("snippet", "")
                    clean_snippet = re.sub(r"<[^>]+>", "", raw_snippet).strip()
                    page_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
                    if title and clean_snippet:
                        results.append({
                            "title": f"{title} - Wikipedia",
                            "url": page_url,
                            "source_name": "Wikipedia",
                            "snippet": clean_snippet
                        })
    except Exception as e:
        logger.debug(f"[Wikipedia API] Fallback error: {e}")
    return results

def get_cache_ttl_for_query(query: str) -> int:
    """Returns dynamic cache TTL in seconds based on query volatility."""
    q_low = query.lower()
    if re.search(r"\b(weather|temperature|stock|price|score|match|live)\b", q_low):
        return 180  # 3 minutes for volatile data
    if re.search(r"\b(festival|diwali|holi|eid|christmas|calendar|version|history)\b", q_low):
        return 1800  # 30 minutes for calendar/stable version facts
    return 600  # 10 minutes default

def perform_web_search(
    query: str,
    max_results: int = 5,
    client_timezone: str = "Asia/Kolkata"
) -> List[Dict[str, str]]:
    """
    Executes resilient, multi-engine web search with domain authority ranking,
    content quality filtering, and intelligent caching.
    """
    decision = classify_query_intent(query, client_timezone=client_timezone)
    search_query = decision.optimized_query
    cache_key = re.sub(r"\W+", "", search_query.lower())
    now = time.time()
    ttl = get_cache_ttl_for_query(search_query)

    # 1. Check cache
    with _CACHE_LOCK:
        if cache_key in _SEARCH_CACHE:
            entry = _SEARCH_CACHE[cache_key]
            if now - entry["timestamp"] < ttl:
                logger.info(f"[WebSearch] Cache hit for '{search_query}' (TTL {ttl}s)")
                return entry["results"]

    raw_sources: List[Dict[str, str]] = []

    # 2. Execute Primary Engine: DDGS Multi-Engine Search
    raw_sources.extend(_search_ddgs_multi(search_query, max_results=max_results + 2))

    # 3. Fallback to DDG HTML if primary engine yielded insufficient results
    if len(raw_sources) < 2:
        html_results = _search_ddg_html(search_query, max_results=max_results)
        raw_sources.extend(html_results)

    # 4. Fallback to Wikipedia Knowledge API if still insufficient
    if len(raw_sources) < 2:
        wiki_results = _search_wikipedia_api(search_query, max_results=3)
        raw_sources.extend(wiki_results)

    # 5. Score, filter low-quality domains, and re-rank by domain authority
    final_sources = rank_and_deduplicate_sources(raw_sources, search_query, max_results=max_results)

    # 6. Save in cache
    with _CACHE_LOCK:
        _SEARCH_CACHE[cache_key] = {
            "timestamp": now,
            "results": final_sources
        }
        # Maintain cache size limit
        if len(_SEARCH_CACHE) > 250:
            oldest = sorted(_SEARCH_CACHE.keys(), key=lambda k: _SEARCH_CACHE[k]["timestamp"])[:50]
            for k in oldest:
                _SEARCH_CACHE.pop(k, None)

    logger.info(f"[WebSearch] Retrieved {len(final_sources)} authoritative sources for '{search_query}'")
    return final_sources
