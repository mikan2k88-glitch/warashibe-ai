from __future__ import annotations

from .shadow_collector import collect_shadow_observations


def collect_from_providers(providers: list, *, max_items_per_provider: int = 200, repository=None) -> dict:
    provider_results = []
    all_observations = []
    failed = 0

    for provider in providers:
        result = collect_shadow_observations(
            provider,
            max_items=max_items_per_provider,
            repository=repository,
        )
        provider_results.append({
            "provider_name": getattr(provider, "provider_name", "unknown"),
            "status": result["status"],
            "health": result["health"],
            "observation_count": len(result["observations"]),
        })
        all_observations.extend(result["observations"])
        if result["status"] == "blocked":
            failed += 1

    return {
        "status": "completed" if failed < len(providers) else "blocked",
        "provider_count": len(providers),
        "failed_provider_count": failed,
        "observation_count": len(all_observations),
        "observations": all_observations,
        "providers": provider_results,
        "external_writes": False,
        "live_execution_allowed": False,
    }
