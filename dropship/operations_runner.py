from __future__ import annotations

from .persistence_health import assess_persistence_environment
from .real_shadow_controller import run_real_shadow_controller
from .supabase_persistence import (
    load_observation_history,
    persist_observations,
    persist_run,
)


def run_persistent_real_shadow(
    supplier_provider,
    market_provider,
    *,
    persistence_client=None,
    supplier_currency: str = "USD",
    target_currency: str | None = None,
    fx_rates: dict | None = None,
    budget: dict | None = None,
    shadow_thresholds: dict | None = None,
    mode: str = "real_read",
    history_limit: int = 1000,
) -> dict:
    persistence = assess_persistence_environment()

    history = []
    history_loaded = False
    persistence_errors = []

    if persistence_client is not None:
        try:
            history = load_observation_history(
                persistence_client,
                limit=history_limit,
            )
            history_loaded = True
        except Exception as exc:
            persistence_errors.append({
                "stage": "load_history",
                "error": str(exc),
            })

    controller = run_real_shadow_controller(
        supplier_provider,
        market_provider,
        historical_observations=history,
        supplier_currency=supplier_currency,
        target_currency=target_currency,
        fx_rates=fx_rates,
        budget=budget,
        shadow_thresholds=shadow_thresholds,
        mode=mode,
    )

    persistence_result = {
        "observations": None,
        "run": None,
    }

    if persistence_client is not None:
        try:
            persistence_result["observations"] = persist_observations(
                persistence_client,
                controller.get("current_observations") or [],
            )
        except Exception as exc:
            persistence_errors.append({
                "stage": "persist_observations",
                "error": str(exc),
            })

        try:
            persistence_result["run"] = persist_run(
                persistence_client,
                controller.get("real_read") or {},
                mode=mode,
            )
        except Exception as exc:
            persistence_errors.append({
                "stage": "persist_run",
                "error": str(exc),
            })

    return {
        "status": controller.get("status"),
        "controller": controller,
        "persistence_environment": persistence,
        "history_loaded": history_loaded,
        "history_count": len(history),
        "persistence_result": persistence_result,
        "persistence_errors": persistence_errors,
        "research_persistence_enabled": persistence_client is not None,
        "commerce_external_writes": False,
        "live_execution_allowed": False,
    }
