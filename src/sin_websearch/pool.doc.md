# `pool.py` — SerpAPI Key Pool Manager

What: Round-robin key pool with 429 cooldown and 401/403 suspension.

## Dependency Map

- Imported by `client.py` (search requests)
- Imported by `mcp_server.py` (status tool)
- Imported by `scripts/websearch-pool.sh` (CLI wrapper)

## Config Values

| Constant | Default | Meaning |
|----------|---------|---------|
| `DEFAULT_COOLDOWN_SECONDS` | 60 | Cooldown after HTTP 429 |
| `INFISICAL_PROJECT` | `fa7758b4-f84c-4297-966e-710056d531ef` | Infisical project ID |
| `INFISICAL_ENV` | `dev` | Infisical environment |

## Usage

```python
from sin_websearch.pool import SerpAPIKeyPool
pool = SerpAPIKeyPool()
pool.load_from_infisical()  # loads SERPAPI_KEY_1..4
key = pool.next_key()
```

## Caveats

- `load_from_infisical()` requires `infisical` CLI on PATH and valid login.
- Keys are stored in memory in plaintext; process memory is the trust boundary.
