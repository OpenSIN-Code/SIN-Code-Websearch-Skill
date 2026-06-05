# `__init__.py` — Package Entry

What: Exports the four public classes of the `sin_websearch` package.

## Dependency Map

- Re-exports from `pool.py`, `cache.py`, `history.py`, `client.py`
- Used by external consumers and tests.

## Usage

```python
from sin_websearch import SerpAPIClient, SerpAPIKeyPool
```
