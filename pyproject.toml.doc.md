# sin-websearch/pyproject.toml

**Purpose:** Build configuration and package metadata for the
`sin-websearch` Python package. Defines the SerpAPI multi-key pool
client, the MCP server, and the optional dev dependencies.

**Source file:** `pyproject.toml` (TOML)

**Header excerpt:**

```
# Purpose: Build configuration for sin-websearch package
# Docs: pyproject.toml.doc.md

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
```

---

## What it does

Declares the package as a PEP 621 Python project using the setuptools
build backend. Pins the minimum Python version (3.10), exposes the
MCP server CLI entry point, and lists the runtime and dev dependencies.

## Dependencies

| Group | Package | Why |
|---|---|---|
| runtime | `requests>=2.31.0` | SerpAPI HTTP client (stable, well-known) |
| runtime | `fastmcp>=0.3.0` | MCP server framework |
| dev | `pytest>=7.0.0` | Test runner |
| dev | `pytest-asyncio>=0.21.0` | Async test support |
| dev | `responses>=0.23.0` | Mock SerpAPI responses in tests |
| dev | `freezegun>=1.0.0` | Mock `time.time()` for rate-limit tests |

## Important config

- `name = "sin-websearch"` — package name on PyPI.
- `version = "1.0.0"` — semantic version; major bump on MCP protocol
  changes.
- `[project.scripts] sin-websearch-server = "mcp_server:main"` —
  exposes the CLI binary that starts the MCP server over stdio.

## Why these decisions

- **setuptools, not hatchling** — sin-websearch predates the
  marketplace skill's switch to hatchling; both work fine.
- **`fastmcp>=0.3.0`** — sin-websearch uses the older fastmcp API
  (`@mcp.tool()` decorator), so it doesn't need 2.0+.
- **`responses` + `freezegun`** — needed for the 62 unit tests
  because SerpAPI requires real API keys and rate-limit logic
  depends on wall-clock time.

## Usage example

```bash
# Install in editable mode for development
pip install -e .[dev]

# Run the test suite
pytest tests/ -v

# Start the MCP server
sin-websearch-server
```

## Known caveats

- **SerpAPI keys via env vars** — the package reads `SERPAPI_KEY_1..4`
  from the environment (or from Infisical, if configured). It will
  start without keys, but every search call will fail.
- **`mcp_server.py` at package root** — the entry point
  `mcp_server:main` refers to the root-level `mcp_server.py`, NOT
  `src/sin_websearch/mcp_server.py`. This is intentional: the MCP
  server is meant to be run as a top-level script, not imported.
