# `websearch-history.sh` — CLI History Wrapper

What: List recent search history from the SQLite database.

## Usage

```bash
scripts/websearch-history.sh [limit] [offset] [query_filter]
```

## Example

```bash
scripts/websearch-history.sh 20 0 "openai"
```

## Caveats

- History DB is stored in `data/websearch_history.db`.
- `key_used` values are masked (e.g., "key_1") to avoid secret leaks.
