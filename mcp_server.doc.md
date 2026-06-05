# `mcp_server.py` — FastMCP Server

What: Exposes 5 websearch tools via FastMCP (Model Context Protocol).

## Tools

| Tool | Purpose |
|------|---------|
| `websearch_search` | Execute a web search via SerpAPI |
| `websearch_status` | Show pool status (keys, cooldown, suspension) |
| `websearch_cache` | Interact with result cache (get/clear/list/size) |
| `websearch_history` | List recent search history |
| `websearch_rate_limit` | Check rate limits and key availability |

## Dependency Map

- Imports `client.py`, `pool.py`, `cache.py`, `history.py`
- Entry point: `python3 mcp_server.py` (stdio transport)

## Startup Behavior

1. Load keys from Infisical (`SERPAPI_KEY_1..4`).
2. If Infisical fails, fall back to environment variables.
3. Create a single `SerpAPIClient` instance shared across all tools.

## Usage

```bash
# Run server
python3 mcp_server.py

# In an MCP client (e.g., OpenCode), call:
# websearch_search("latest AI news")
```

## Caveats

- `websearch_cache` with `action="set"` is a no-op because the client auto-caches on search.
- Uses global `_client` for performance; not thread-safe for re-initialization.
