#!/usr/bin/env bash
# Purpose: CLI history wrapper
# Docs: scripts/websearch-history.doc.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

LIMIT="${1:-50}"
OFFSET="${2:-0}"
QUERY_FILTER="${3:-}"

python3 -c "
import sys, json
sys.path.insert(0, '${PROJECT_ROOT}/src')
from sin_websearch.history import SearchHistory

history = SearchHistory()
entries = history.list(
    limit=${LIMIT},
    offset=${OFFSET},
    query_filter='${QUERY_FILTER}' or None,
)
print(json.dumps({'entries': entries}, indent=2, ensure_ascii=False))
"
