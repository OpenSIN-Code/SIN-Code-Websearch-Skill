# Archive: SIN-Code-Websearch-Skill

This repository is **archived** and has been superseded by the unified `sin-websearch` binary in `OpenSIN-Code/web_search_bundle`.

## What it was

A Python-based MCP skill for OpenCode that provided SerpAPI web search with a multi-key pool, SQLite caching, search history, and rate-limit management.

## What replaced it

- `sin-websearch` (Go binary) in `OpenSIN-Code/web_search_bundle`.
- Exposes `websearch_search`, `websearch_pulse`, `websearch_resolve`, `websearch_watch`, `websearch_video_brief`, `websearch_video_prompt`, and `websearch_alchemist`.
- Includes a built-in HTTP API, MCP server, video intelligence, and autonomous alchemist research loops.

## Why it was archived

The unified Go binary bundles web search, social pulse, entity resolution, video analysis, and multi-agent research missions in a single executable with no Python dependency or venv management.

## Migration

| Old (Python skill) | New (Go binary) |
| --- | --- |
| `websearch_search` | `sin-websearch search` or `websearch_search` MCP tool |
| `websearch_status` | `sin-websearch serve` + health checks |
| `websearch_cache` | `sin-websearch serve` (SQLite cache) |
| `websearch_history` | `sin-websearch serve` (SQLite history) |
| `websearch_rate_limit` | `sin-websearch serve` (key pool) |

## Read-only

No new issues, PRs, or releases are accepted. This repo remains available for historical reference.

See the active repository: https://github.com/OpenSIN-Code/web_search_bundle
