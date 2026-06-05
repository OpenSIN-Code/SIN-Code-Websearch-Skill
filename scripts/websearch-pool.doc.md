# `websearch-pool.sh` — CLI Pool Management

What: Manage the SerpAPI key pool (reset, status).

## Usage

```bash
scripts/websearch-pool.sh status   # Show pool status
scripts/websearch-pool.sh reset    # Reset all keys (clear cooldown/suspension)
```

## Caveats

- `reset` does not re-fetch keys from Infisical; it only clears cooldown/suspension.
