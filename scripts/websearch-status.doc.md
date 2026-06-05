# `websearch-status.sh` — CLI Status Wrapper

What: Print the current SerpAPI key pool status in JSON.

## Usage

```bash
scripts/websearch-status.sh
```

## Output

JSON with `total_keys`, `available_keys`, `cooldown_keys`, `suspended_keys`, and per-key details.

## Caveats

- Keys are masked (`XXXX...XXXX`) for security.
