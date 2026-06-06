# sin-websearch/install.sh

**Purpose:** One-command installer for the sin-websearch skill. Creates
a venv (if needed), installs the package in editable mode with dev
dependencies, and prints usage hints.

**Source file:** `install.sh` (Shell)

**Header excerpt:**

```
#!/usr/bin/env bash
# Purpose: Install sin-websearch skill and dependencies
# Docs: install.sh.doc.md

set -euo pipefail
```

---

## What it does

Performs the standard skill setup:
1. Checks Python version (>= 3.10 required).
2. Installs the package in editable mode with `[dev]` extras.

Fails fast with a clear error if the Python version is too old.

## Dependencies

- `python3` (>= 3.10) — only runtime requirement.
- `pip` — bundled with Python 3.4+, so no separate install needed.
- `pytest` — pulled in via the `[dev]` extra.

## Important config

- **`set -euo pipefail`** — strict mode: exits on any error, undefined
  variable, or pipe failure. This is the safe default for installer
  scripts.
- **Python version check** — uses `sys.version_info` instead of
  string comparison to avoid surprises with versions like "3.10.0rc1".

## Why these decisions

- **Editable mode (`-e`)** — changes to the source code are picked up
  immediately; no need to re-install after every edit.
- **No venv creation** — the installer assumes the user has a
  working Python environment (system Python, venv, or conda). Creating
  a venv from inside an installer is fragile.
- **Usage hints at the end** — prints the two most common next
  commands (test, run server) so newcomers don't have to read the
  README.

## Usage example

```bash
./install.sh
# === SIN-Websearch Skill Installation ===
# === Installed ===
# Run tests: pytest -v
# Run MCP server: python3 mcp_server.py
```

## Known caveats

- **No `--user` flag** — installs into the current environment. If
  you want per-user isolation, activate a venv first:
  `python3 -m venv .venv && source .venv/bin/activate`.
- **PEP 668 systems** — on homebrew Python 3.14+ or Debian 12+,
  you may need `pip install --break-system-packages` or to use a
  venv. The script does NOT handle this automatically.
- **Network required** — pulls `requests`, `fastmcp`, etc. from PyPI.
  Air-gapped installs need a local PyPI mirror.
