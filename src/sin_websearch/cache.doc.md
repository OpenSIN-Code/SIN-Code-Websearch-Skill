# `cache.py` — SQLite Search Result Cache

What: Persistent key-value cache for SerpAPI search results with TTL.

## Dependency Map

- Imported by `client.py` (cache hit/miss logic)
- Imported by `mcp_server.py` (cache tool)
- Imported by `scripts/websearch-cache.sh` (CLI wrapper)

## Config Values

| Constant | Default | Meaning |
|----------|---------|---------|
| `DEFAULT_TTL_SECONDS` | 3600 | Cache entry lifetime (1 hour) |
| `DEFAULT_DB_PATH` | `data/websearch_cache.db` | SQLite database location |

## Usage

```python
from sin_websearch.cache import SearchCache
cache = SearchCache()
cache.set("openai", {"results": [...]})
hit = cache.get("openai")
```

## Caveats

- SQLite file is created automatically; directory `data/` must be writable.
- Expired entries are deleted lazily on `get()` or eagerly via `clear_expired()`.
