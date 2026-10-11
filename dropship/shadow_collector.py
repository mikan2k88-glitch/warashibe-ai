from __future__ import annotations

from .dedupe import deduplicate_observations
from .provider_health import assess_provider_health
from .provider_normalizer import normalize_provider_row


def collect_shadow_observations(provider, *, max_items: int = 200, repository=None) -> dict:
    errors = []
    try:
        fetched = provider.fetch_offers()
    except Exception as exc:
        fetched = []
        errors.append(str(exc))

    limited = list(fetched)[: max(0, int(max_items))]
    normalized = [
        normalize_provider_row(row, provider_name=getattr(provider, "provider_name", "unknown"))
        for row in limited
        if isinstance(row, dict)
    ]
    deduped = deduplicate_observations(normalized)

    persisted = 0
    if repository is not None:
        for row in deduped["unique"]:
            repository.append_observation(row)
            persisted += 1

    health = assess_provider_health(
        fetched=len(limited),
        normalized=len(normalized),
        duplicates=deduped["duplicate_count"],
        errors=errors,
    )
    return {
        "status": "completed" if health["status"] != "blocked" else "blocked",
        "observations": deduped["unique"],
        "duplicate_count": deduped["duplicate_count"],
        "persisted": persisted,
        "health": health,
        "external_writes": False,
        "live_execution_allowed": False,
    }
