# `test_client.py` — Client Tests

What: Unit tests for `SerpAPIClient` and `_extract_results`.

## Coverage

- Success path (200)
- Cache hit (no API call)
- 429 fallback to next key
- 401/403 suspension
- All keys exhausted
- 500 error
- Network error
- History recording
- Rate limit status
- Search parameters (engine, location, language)
- Empty result handling
