# `history.py` — Search History Tracking

What: SQLite-backed persistence of every search attempt with status, key used, and result count.

## Dependency Map

- Imported by `client.py` (records every search)
- Imported by `mcp_server.py` (history tool)
- Imported by `scripts/websearch-history.sh` (CLI wrapper)

## Config Values

| Constant | Default | Meaning |
|----------|---------|---------|
| `DEFAULT_MAX_ENTRIES` | 1000 | Auto-pruning threshold |
| `DEFAULT_DB_PATH` | `data/websearch_history.db` | SQLite database location |

## Usage

```python
from sin_websearch.history import SearchHistory
history = SearchHistory()
history.add("openai", status="success", result_count=10)
entries = history.list(limit=10)
```

## Caveats

- `key_used` should be masked (e.g., "key_1") to avoid leaking secrets in logs.
- Auto-pruning keeps the most recent `max_entries` rows.
