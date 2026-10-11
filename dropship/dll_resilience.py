from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .dll_concierge_client import fetch_registry


@dataclass
class RegistryCache:
    registry: object | None = None
    fetched_at: str | None = None
    failures: int = 0
    last_error: str | None = None

    def store(self, registry):
        self.registry = registry
        self.fetched_at = datetime.now(timezone.utc).isoformat()
        self.failures = 0
        self.last_error = None

    def fail(self, exc: Exception):
        self.failures += 1
        self.last_error = str(exc)


def fetch_registry_resilient(cache: RegistryCache | None = None) -> dict:
    cache = cache or RegistryCache()
    try:
        registry = fetch_registry()
        cache.store(registry)
        return {
            "status": "ok",
            "source": "live",
            "registry": registry,
            "cache": {
                "fetched_at": cache.fetched_at,
                "failures": cache.failures,
            },
        }
    except Exception as exc:
        cache.fail(exc)
        if cache.registry is not None:
            return {
                "status": "degraded",
                "source": "cache",
                "registry": cache.registry,
                "cache": {
                    "fetched_at": cache.fetched_at,
                    "failures": cache.failures,
                    "last_error": cache.last_error,
                },
            }
        return {
            "status": "unavailable",
            "source": "none",
            "registry": None,
            "cache": {
                "fetched_at": cache.fetched_at,
                "failures": cache.failures,
                "last_error": cache.last_error,
            },
        }
