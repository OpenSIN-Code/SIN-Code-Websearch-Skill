# `client.py` — SerpAPI Client

What: High-level search client that orchestrates pool, cache, and history.

## Dependency Map

- Imports `pool.py`, `cache.py`, `history.py`
- Imported by `mcp_server.py` (all search tools)
- Imported by `scripts/websearch-search.sh` (CLI wrapper)

## Config Values

| Constant | Default | Meaning |
|----------|---------|---------|
| `SERPAPI_BASE_URL` | `https://serpapi.com/search` | API endpoint |
| `DEFAULT_ENGINE` | `google` | Default search engine |
| `DEFAULT_TIMEOUT` | 15s | Request timeout |

## Usage

```python
from sin_websearch.client import SerpAPIClient
client = SerpAPIClient()
client.pool.load_from_infisical()
result = client.search("openai")
```

## Flow

1. Check cache → return cached results if hit.
2. Get next key from pool.
3. Call SerpAPI.
4. On 429: cooldown key, retry with next key.
5. On 401/403: suspend key, retry with next key.
6. On success: cache result, record history, return.

## Caveats

- `search()` is blocking (synchronous). The MCP server wraps it in threads.
- `_extract_results()` is engine-specific; add more engines as needed.
