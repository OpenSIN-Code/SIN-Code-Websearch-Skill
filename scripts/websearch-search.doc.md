# `websearch-search.sh` — CLI Search Wrapper

What: Bash script wrapper around `sin_websearch.client.SerpAPIClient.search()`.

## Usage

```bash
scripts/websearch-search.sh "openai" --engine=google --num=10
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--engine` | `google` | Search engine |
| `--num` | `10` | Number of results |
| `--location` | "" | Geographic location |
| `--language` | "" | Language code |

## Caveats

- Loads keys from Infisical or env vars on every invocation (slow).
- For repeated use, prefer the MCP server or Python API.
