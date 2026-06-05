---
name: sin-websearch
description: "Websearch via SerpAPI — multi-key pool, caching, history"
version: 1.0.0
category: productivity
requirements:
  - infisical CLI (for key loading)
  - SerpAPI keys in Infisical or env vars
---

# SIN-Websearch Skill

Universal web search for agents. Loads API keys from Infisical, rotates on 429, caches results, and tracks history.

## Commands

```bash
# MCP server
python3 mcp_server.py

# CLI search
scripts/websearch-search.sh "latest AI news" --num=10

# Pool status
scripts/websearch-status.sh

# Cache management
scripts/websearch-cache.sh clear

# History
scripts/websearch-history.sh 20
```

## Infisical Project

| Field | Value |
|-------|-------|
| Project ID | `fa7758b4-f84c-4297-966e-710056d531ef` |
| Environment | `dev` |
| Path | `/` |
| Secrets | `SERPAPI_KEY_1` .. `SERPAPI_KEY_4` |

## Installation

```bash
git clone https://github.com/OpenSIN-Code/SIN-Code-Websearch-Skill.git
cd SIN-Code-Websearch-Skill
bash install.sh
```

## MCP Provider Config

Add to `~/.config/opencode/opencode.json`:

```json
{
  "mcpServers": {
    "sin-websearch": {
      "command": "python3",
      "args": ["/path/to/SIN-Code-Websearch-Skill/mcp_server.py"]
    }
  }
}
```
