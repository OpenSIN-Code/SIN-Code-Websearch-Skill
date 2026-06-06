#!/usr/bin/env bash
# Purpose: CLI cache management
# Docs: websearch-cache.doc.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ACTION="${1:-size}"
QUERY="${2:-}"

python3 -c "
import sys, json
sys.path.insert(0, '${PROJECT_ROOT}/src')
from sin_websearch.cache import SearchCache

cache = SearchCache()
action = '${ACTION}'
if action == 'size':
    print(json.dumps({'size': cache.size()}, indent=2))
elif action == 'clear':
    count = cache.clear()
    print(json.dumps({'cleared': count}, indent=2))
elif action == 'list':
    queries = cache.list_queries()
    print(json.dumps({'queries': queries}, indent=2))
elif action == 'get':
    query = '${QUERY}'
    if not query:
        print('Usage: websearch-cache.sh get <query>', file=sys.stderr)
        sys.exit(1)
    val = cache.get(query)
    print(json.dumps({'hit': val is not None, 'result': val}, indent=2))
else:
    print(f'Unknown action: {action}', file=sys.stderr)
    sys.exit(1)
"
