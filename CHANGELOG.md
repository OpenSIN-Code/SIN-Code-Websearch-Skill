# Changelog

## 1.0.0 — 2026-06-05

### Added
- MCP server (FastMCP) with 5 tools: search, status, cache, history, rate_limit
- `SerpAPIClient` with multi-key pool, caching, and history tracking
- `SerpAPIKeyPool` — round-robin, 429 cooldown, 401/403 suspension
- `SearchCache` — SQLite-backed TTL cache
- `SearchHistory` — SQLite-backed persistent history with auto-pruning
- Bash CLI wrappers: search, status, pool, cache, history
- 40+ pytest tests covering pool, cache, history, client, and MCP tools
- 100% CoDocs coverage (.doc.md companions for every .py file)
- `.github/workflows/ceo-audit.yml` — 47-gate SOTA audit
- `SIN_GITHUB_FALLBACK_TOKEN` repo secret

### Infrastructure
- Template based on `SIN-Code-Infisical-Bundle`
- Infisical integration for key loading (`SERPAPI_KEY_1..4`)
- Python 3.10+ support
