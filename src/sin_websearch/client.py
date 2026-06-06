"""SerpAPI client with multi-key pool, caching, and history tracking.

Docs: client.doc.md
"""

import json
import time
from typing import Optional

import requests

from .cache import SearchCache
from .history import SearchHistory
from .pool import SerpAPIKeyPool

# ── Constants ──────────────────────────────────────
SERPAPI_BASE_URL = "https://serpapi.com/search"
DEFAULT_ENGINE = "google"
DEFAULT_TIMEOUT = 15


class SerpAPIClient:
    """High-level SerpAPI client wrapping the key pool, cache, and history.

    Attributes:
        pool: Key pool for round-robin + fallback.
        cache: Result cache to avoid duplicate API calls.
        history: Persistent history of all search attempts.
    """

    def __init__(
        self,
        pool: Optional[SerpAPIKeyPool] = None,
        cache: Optional[SearchCache] = None,
        history: Optional[SearchHistory] = None,
    ):
        self.pool = pool or SerpAPIKeyPool()
        self.cache = cache or SearchCache()
        self.history = history or SearchHistory()

    def search(
        self,
        query: str,
        engine: str = DEFAULT_ENGINE,
        num_results: int = 10,
        location: Optional[str] = None,
        language: Optional[str] = None,
    ) -> dict:
        """Execute a web search with pool failover and caching.

        Args:
            query: The search query string.
            engine: Search engine (default "google").
            num_results: Number of results to request.
            location: Optional geographic location.
            language: Optional language code.

        Returns:
            A dict with keys: success (bool), results (list), source (str),
            query (str), and optionally error (str).
        """
        # 1. Check cache
        cached = self.cache.get(query)
        if cached is not None:
            self.history.add(
                query=query,
                status="cached",
                result_count=len(cached.get("results", [])),
            )
            return {
                "success": True,
                "results": cached.get("results", []),
                "source": "cache",
                "query": query,
            }

        # 2. Try pool keys
        tried_keys = 0
        while True:
            key = self.pool.next_key()
            if key is None:
                self.history.add(
                    query=query,
                    status="error",
                    error_message="All keys in cooldown or suspended",
                )
                return {
                    "success": False,
                    "error": "All keys in cooldown or suspended. Please wait and retry.",
                    "query": query,
                }

            tried_keys += 1
            params = {
                "q": query,
                "engine": engine,
                "num": num_results,
                "api_key": key,
            }
            if location:
                params["location"] = location
            if language:
                params["hl"] = language

            try:
                resp = requests.get(
                    SERPAPI_BASE_URL,
                    params=params,
                    timeout=DEFAULT_TIMEOUT,
                )
            except requests.RequestException as exc:
                self.history.add(
                    query=query,
                    status="error",
                    error_message=str(exc),
                )
                return {
                    "success": False,
                    "error": f"Network error: {exc}",
                    "query": query,
                }

            if resp.status_code == 200:
                data = resp.json()
                results = _extract_results(data)
                self.cache.set(query, {"results": results})
                self.history.add(
                    query=query,
                    status="success",
                    key_used=f"key_{tried_keys}",
                    result_count=len(results),
                )
                return {
                    "success": True,
                    "results": results,
                    "source": "api",
                    "query": query,
                }

            if resp.status_code == 429:
                # Rate limited: cooldown this key and try next
                self.pool.report_rate_limit(key)
                self.history.add(
                    query=query,
                    status="rate_limited",
                    key_used=f"key_{tried_keys}",
                    error_message="HTTP 429",
                )
                continue

            if resp.status_code in (401, 403):
                # Key invalid: suspend permanently
                self.pool.report_suspended(key)
                self.history.add(
                    query=query,
                    status="error",
                    key_used=f"key_{tried_keys}",
                    error_message=f"HTTP {resp.status_code}",
                )
                continue

            # Other error (e.g., 500) — treat as fatal for this request
            self.history.add(
                query=query,
                status="error",
                key_used=f"key_{tried_keys}",
                error_message=f"HTTP {resp.status_code}",
            )
            return {
                "success": False,
                "error": f"SerpAPI error {resp.status_code}: {resp.text[:200]}",
                "query": query,
            }

    def rate_limit_status(self) -> dict:
        """Return current rate-limit status from the pool."""
        return self.pool.status()


def _extract_results(data: dict) -> list[dict]:
    """Normalize SerpAPI JSON into a list of result dicts.

    Handles both "organic_results" (Google) and "results" fallback.
    """
    organic = data.get("organic_results", [])
    if organic:
        return [
            {
                "title": r.get("title", ""),
                "link": r.get("link", ""),
                "snippet": r.get("snippet", ""),
            }
            for r in organic
        ]
    # Fallback: any list of dicts with title/link
    fallback = data.get("results", [])
    if isinstance(fallback, list):
        return [
            {
                "title": r.get("title", ""),
                "link": r.get("link", ""),
                "snippet": r.get("snippet", ""),
            }
            for r in fallback
        ]
    return []
