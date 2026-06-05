#!/usr/bin/env bash
# Purpose: Install sin-websearch skill and dependencies
# Docs: install.sh.doc.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== SIN-Websearch Skill Installation ==="

# Ensure Python >= 3.10
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' 2>/dev/null || echo "0")
if [ "$(python3 -c "print(int('$PYTHON_VERSION'.replace('.','')) >= 310)" 2>/dev/null || echo "False")" != "True" ]; then
    echo "[ERROR] Python >= 3.10 required. Found: $PYTHON_VERSION"
    exit 1
fi

# Install package in editable mode
python3 -m pip install -e "$SCRIPT_DIR"[dev]

echo "=== Installed ==="
echo "Run tests: pytest -v"
echo "Run MCP server: python3 mcp_server.py"
