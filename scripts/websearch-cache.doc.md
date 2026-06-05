# `websearch-cache.sh` — CLI Cache Management

What: Manage the SQLite search result cache.

## Usage

```bash
scripts/websearch-cache.sh size       # Number of cached entries
scripts/websearch-cache.sh clear      # Delete all entries
scripts/websearch-cache.sh list       # List cached queries
scripts/websearch-cache.sh get <query>  # Check if query is cached
```

## Caveats

- Cache DB is stored in `data/websearch_cache.db`.
