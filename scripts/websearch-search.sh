#!/usr/bin/env bash
# Purpose: CLI wrapper for web search via sin-websearch
# Docs: websearch-search.doc.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

QUERY=""
ENGINE="google"
NUM_RESULTS=10
LOCATION=""
LANGUAGE=""

usage() {
    echo "Usage: $(basename "$0") <query> [--engine=google] [--num=10] [--location=...] [--language=...]"
    exit 1
}

# Parse args
if [ $# -lt 1 ]; then usage; fi
QUERY="$1"
shift

while [ $# -gt 0 ]; do
    case "$1" in
        --engine=*) ENGINE="${1#*=}" ;;
        --num=*) NUM_RESULTS="${1#*=}" ;;
        --location=*) LOCATION="${1#*=}" ;;
        --language=*) LANGUAGE="${1#*=}" ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
    shift
done

# Run via Python module
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
result = client.search(
    query='${QUERY}',
    engine='${ENGINE}',
    num_results=${NUM_RESULTS},
    location='${LOCATION}' or None,
    language='${LANGUAGE}' or None,
)
print(json.dumps(result, indent=2, ensure_ascii=False))
"
