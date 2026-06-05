#!/usr/bin/env bash
# Purpose: CLI pool management (reset, reload, manual add)
# Docs: scripts/websearch-pool.doc.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ACTION="${1:-status}"

python3 -c "
import sys, json, os
sys.path.insert(0, '${PROJECT_ROOT}/src')
from sin_websearch.pool import SerpAPIKeyPool

pool = SerpAPIKeyPool()
loaded = pool.load_from_infisical()
if loaded == 0:
    env_keys = [os.environ.get(f'SERPAPI_KEY_{i}') for i in range(1,5)]
    env_keys = [k for k in env_keys if k]
    if env_keys:
        pool = SerpAPIKeyPool(env_keys)

action = '${ACTION}'
if action == 'reset':
    pool.reset_all()
    print(json.dumps({'ok': True, 'message': 'All keys reset'}, indent=2))
elif action == 'status':
    print(json.dumps(pool.status(), indent=2, ensure_ascii=False))
else:
    print(f'Unknown action: {action}', file=sys.stderr)
    sys.exit(1)
"
