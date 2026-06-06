"""SerpAPI key pool manager with round-robin, 429 fallback, and cooldown.

Docs: pool.doc.md
"""

import os
import subprocess
import time
from typing import Optional

# ── Constants ──────────────────────────────────────
DEFAULT_COOLDOWN_SECONDS = 60
INFISICAL_PROJECT = os.environ.get(
    "INFISICAL_PROJECT_ID", "fa7758b4-f84c-4297-966e-710056d531ef"
)
INFISICAL_ENV = os.environ.get("INFISICAL_ENV", "dev")
INFISICAL_PATH = os.environ.get("INFISICAL_PATH", "/")
INFISICAL_TIMEOUT = int(os.environ.get("INFISICAL_TIMEOUT", "15"))


class KeyInfo:
    """Metadata for a single SerpAPI key."""

    def __init__(self, key: str, index: int):
        self.key = key
        self.index = index
        self.cooldown_until: float = 0.0
        self.suspended = False
        self.last_used: float = 0.0
        self.use_count = 0

    @property
    def is_available(self) -> bool:
        """Return True if the key is not suspended and not in cooldown."""
        if self.suspended:
            return False
        return time.time() >= self.cooldown_until

    def mark_cooldown(self, seconds: int = DEFAULT_COOLDOWN_SECONDS) -> None:
        """Put the key on cooldown (e.g., after a 429)."""
        self.cooldown_until = time.time() + seconds

    def mark_suspended(self) -> None:
        """Permanently suspend the key (e.g., after 401/403)."""
        self.suspended = True

    def reset(self) -> None:
        """Clear cooldown and suspension."""
        self.cooldown_until = 0.0
        self.suspended = False


class SerpAPIKeyPool:
    """Manages a pool of SerpAPI keys with round-robin and 429 fallback.

    Attributes:
        keys: List of KeyInfo objects in pool order.
        current_index: Next key to hand out (round-robin pointer).
    """

    def __init__(self, keys: Optional[list[str]] = None):
        if keys:
            self.keys = [KeyInfo(k, i) for i, k in enumerate(keys)]
        else:
            self.keys = []
        self.current_index = 0

    # ── Key loading ──────────────────────────────────────

    def load_from_infisical(self, key_names: Optional[list[str]] = None) -> int:
        """Load keys from Infisical using the CLI.

        Args:
            key_names: List of secret names to fetch. Defaults to
                       SERPAPI_KEY_1..4.

        Returns:
            Number of keys successfully loaded.
        """
        if key_names is None:
            key_names = [f"SERPAPI_KEY_{i}" for i in range(1, 5)]
        loaded = 0
        for name in key_names:
            value = _infisical_get(name)
            if value:
                self.keys.append(KeyInfo(value, len(self.keys)))
                loaded += 1
        return loaded

    # ── Pool operations ──────────────────────────────────────

    def next_key(self) -> Optional[str]:
        """Return the next available key (round-robin).

        Skips keys in cooldown or suspended. If no key is available,
        returns None.
        """
        for _ in range(len(self.keys)):
            key_info = self.keys[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.keys)
            if key_info.is_available:
                key_info.last_used = time.time()
                key_info.use_count += 1
                return key_info.key
        return None

    def report_rate_limit(self, key: str) -> None:
        """Mark a key as rate-limited (429) and put it on cooldown."""
        for ki in self.keys:
            if ki.key == key:
                ki.mark_cooldown()
                break

    def report_suspended(self, key: str) -> None:
        """Mark a key as suspended (401/403)."""
        for ki in self.keys:
            if ki.key == key:
                ki.mark_suspended()
                break

    def reset_key(self, key: str) -> None:
        """Reset cooldown and suspension for a key."""
        for ki in self.keys:
            if ki.key == key:
                ki.reset()
                break

    def reset_all(self) -> None:
        """Reset all keys in the pool."""
        for ki in self.keys:
            ki.reset()

    # ── Status ──────────────────────────────────────

    def status(self) -> dict:
        """Return JSON-serializable pool status."""
        now = time.time()
        return {
            "total_keys": len(self.keys),
            "available_keys": sum(1 for k in self.keys if k.is_available),
            "cooldown_keys": sum(
                1 for k in self.keys if not k.suspended and now < k.cooldown_until
            ),
            "suspended_keys": sum(1 for k in self.keys if k.suspended),
            "keys": [
                {
                    "index": k.index,
                    "masked": f"{k.key[:4]}...{k.key[-4:]}",
                    "available": k.is_available,
                    "cooldown_seconds": max(0, k.cooldown_until - now)
                    if k.cooldown_until > now
                    else 0,
                    "suspended": k.suspended,
                    "use_count": k.use_count,
                    "last_used": k.last_used,
                }
                for k in self.keys
            ],
        }


# ── Infisical helper ──────────────────────────────────────


def _infisical_get(key: str) -> Optional[str]:
    """Fetch a single secret from Infisical via CLI."""
    try:
        result = subprocess.run(
            [
                "infisical",
                "secrets",
                "get",
                key,
                "--projectId",
                INFISICAL_PROJECT,
                "--env",
                INFISICAL_ENV,
                "--path",
                INFISICAL_PATH,
                "--plain",
                "--silent",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=INFISICAL_TIMEOUT,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None
