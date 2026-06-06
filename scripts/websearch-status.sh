#!/usr/bin/env bash
# Purpose: CLI wrapper for pool status
# Docs: websearch-status.doc.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

python3 -c "
import sys, json
sys.path.insert(0, '${PROJECT_ROOT}/src')
from sin_websearch.client import SerpAPIClient
from sin_websearch.pool import SerpAPIKeyPool

pool = SerpAPIKeyPool()
loaded = pool.load_from_infisical()
if loaded == 0:
    import os
    env_keys = [os.environ.get(f'SERPAPI_KEY_{i}') for i in range(1,5)]
    env_keys = [k for k in env_keys if k]
    if env_keys:
        pool = SerpAPIKeyPool(env_keys)

client = SerpAPIClient(pool=pool)
print(json.dumps(client.pool.status(), indent=2, ensure_ascii=False))
"
