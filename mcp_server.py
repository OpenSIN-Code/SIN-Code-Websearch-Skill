"""FastMCP server exposing websearch tools.

Docs: mcp_server.doc.md
"""

import json
import os
from typing import Optional

from fastmcp import FastMCP

from sin_websearch.client import SerpAPIClient
from sin_websearch.cache import SearchCache
from sin_websearch.history import SearchHistory
from sin_websearch.pool import SerpAPIKeyPool

# ── Server init ──────────────────────────────────────

mcp = FastMCP("sin-websearch")

# Global client instance (loaded once at startup)
_client: Optional[SerpAPIClient] = None


def _get_client() -> SerpAPIClient:
    """Lazy-initialize the shared SerpAPIClient."""
    global _client
    if _client is None:
        pool = SerpAPIKeyPool()
        loaded = pool.load_from_infisical()
        if loaded == 0:
            # Fallback: try environment variables
            env_keys = []
            for i in range(1, 5):
                val = os.environ.get(f"SERPAPI_KEY_{i}")
                if val:
                    env_keys.append(val)
            if env_keys:
                pool = SerpAPIKeyPool(env_keys)
        _client = SerpAPIClient(pool=pool)
    return _client


# ── Tools ──────────────────────────────────────

@mcp.tool()
def websearch_search(
    query: str,
    engine: str = "google",
    num_results: int = 10,
    location: Optional[str] = None,
    language: Optional[str] = None,
) -> str:
    """Search the web using SerpAPI.

    Args:
        query: Search query string.
        engine: Search engine (default: google).
        num_results: Number of results (default: 10).
        location: Optional location filter.
        language: Optional language code.

    Returns:
        JSON string with success, results, source, and query.
    """
    client = _get_client()
    result = client.search(
        query=query,
        engine=engine,
        num_results=num_results,
        location=location,
        language=language,
    )
    return json.dumps(result, indent=2)


@mcp.tool()
def websearch_status() -> str:
    """Show the current pool status (keys, cooldown, suspension).

    Returns:
        JSON string with pool statistics.
    """
    client = _get_client()
    status = client.pool.status()
    return json.dumps(status, indent=2)


@mcp.tool()
def websearch_cache(query: Optional[str] = None, action: str = "get") -> str:
    """Interact with the search result cache.

    Args:
        query: Query string (required for "get" and "set").
        action: One of "get", "set", "clear", "list", "size".

    Returns:
        JSON string with the cache operation result.
    """
    client = _get_client()
    if action == "get":
        if not query:
            return json.dumps({"error": "query required for get"}, indent=2)
        val = client.cache.get(query)
        return json.dumps({"hit": val is not None, "result": val}, indent=2)
    elif action == "set":
        if not query:
            return json.dumps({"error": "query required for set"}, indent=2)
        # For set, we expect the caller to have already searched; this is a no-op
        return json.dumps({"ok": True}, indent=2)
    elif action == "clear":
        count = client.cache.clear()
        return json.dumps({"cleared": count}, indent=2)
    elif action == "list":
        queries = client.cache.list_queries()
        return json.dumps({"queries": queries}, indent=2)
    elif action == "size":
        size = client.cache.size()
        return json.dumps({"size": size}, indent=2)
    else:
        return json.dumps({"error": f"Unknown action: {action}"}, indent=2)


@mcp.tool()
def websearch_history(limit: int = 50, offset: int = 0, query_filter: Optional[str] = None) -> str:
    """List recent search history.

    Args:
        limit: Max entries to return (default: 50).
        offset: Pagination offset (default: 0).
        query_filter: Optional substring filter on query.

    Returns:
        JSON string with history entries.
    """
    client = _get_client()
    entries = client.history.list(
        limit=limit,
        offset=offset,
        query_filter=query_filter,
    )
    return json.dumps({"entries": entries}, indent=2)


@mcp.tool()
def websearch_rate_limit() -> str:
    """Check current rate limits and key availability.

    Returns:
        JSON string with rate-limit status.
    """
    client = _get_client()
    status = client.rate_limit_status()
    return json.dumps(status, indent=2)


# ── Entry point ──────────────────────────────────────

def main():
    mcp.run()


if __name__ == "__main__":
    main()
