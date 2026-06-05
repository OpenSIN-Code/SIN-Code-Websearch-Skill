# SIN-Code-Websearch-Skill

MCP Websearch Skill for OpenCode — SerpAPI multi-key pool with caching, history, and rate-limit management.

## Features

- **Multi-key pool**: 4 SerpAPI keys with round-robin and 429 fallback
- **Caching**: SQLite-based deduplication to avoid duplicate API calls
- **History**: Persistent search history with status tracking
- **MCP Server**: 5 tools exposed via FastMCP
- **CLI**: Bash wrappers for direct terminal usage
- **CoDocs**: 100% documentation coverage

## Quick Start

```bash
git clone https://github.com/OpenSIN-Code/SIN-Code-Websearch-Skill.git
cd SIN-Code-Websearch-Skill
bash install.sh
pytest -v
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `websearch_search` | Search the web via SerpAPI |
| `websearch_status` | Show key pool status |
| `websearch_cache` | Manage result cache |
| `websearch_history` | List recent searches |
| `websearch_rate_limit` | Check rate limits |

## CLI Scripts

```bash
scripts/websearch-search.sh "openai" --num=10
scripts/websearch-status.sh
scripts/websearch-pool.sh reset
scripts/websearch-cache.sh clear
scripts/websearch-history.sh 20
```

## Architecture

```
MCP Client (OpenCode)
    ↓ FastMCP (stdio)
mcp_server.py
    ↓ SerpAPIClient
    ├─ SerpAPIKeyPool (round-robin, 429 fallback)
    ├─ SearchCache (SQLite)
    └─ SearchHistory (SQLite)
        ↓ SerpAPI
```

## Key Pool

Keys are loaded from Infisical (`fa7758b4-f84c-4297-966e-710056d531ef`) or environment variables:

```bash
export SERPAPI_KEY_1="..."
export SERPAPI_KEY_2="..."
export SERPAPI_KEY_3="..."
export SERPAPI_KEY_4="..."
```

## Tests

```bash
pytest -v
```

40+ tests covering pool rotation, 429 fallback, cache hit/miss, history tracking, and rate limiting.

## License

MIT — OpenSIN Code
