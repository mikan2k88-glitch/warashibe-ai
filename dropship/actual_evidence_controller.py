from __future__ import annotations

from .operations_runner import run_persistent_real_shadow
from .promotion_queue import build_promotion_queue
from .promotion_review_v52 import build_v52_promotion_review
from .real_product_ranking import rank_real_products
from .shadow_metrics import build_shadow_metrics
from .supabase_persistence import load_observation_history, load_recent_runs
from .v61_real_gate import build_v61_real_gate


def run_actual_evidence_controller(
    supplier_provider,
    market_provider,
    *,
    persistence_client,
    provider_handshake: dict,
    available_capital: float = 3000,
    supplier_currency: str = "USD",
    target_currency: str | None = None,
    fx_rates: dict | None = None,
    budget: dict | None = None,
    shadow_thresholds: dict | None = None,
    history_limit: int = 2000,
    run_limit: int = 200,
) -> dict:
    if persistence_client is None:
        return {
            "controller_version": "6.2",
            "status": "setup_required",
            "reason": "persistent_shadow_required",
            "human_gate_ready_count": 0,
            "live_execution_allowed": False,
        }

    if provider_handshake.get("status") != "real_provider_handshake_ready":
        return {
            "controller_version": "6.2",
            "status": "setup_required",
            "reason": "provider_handshake_required",
            "human_gate_ready_count": 0,
            "live_execution_allowed": False,
        }

    operation = run_persistent_real_shadow(
        supplier_provider,
        market_provider,
        persistence_client=persistence_client,
        supplier_currency=supplier_currency,
        target_currency=target_currency,
        fx_rates=fx_rates,
        budget=budget,
        shadow_thresholds=shadow_thresholds,
        mode="real_read",
        history_limit=history_limit,
    )

    real_read = (operation.get("controller") or {}).get("real_read") or {}
    raw_ranked = (real_read.get("ranking") or {}).get("ranked") or []
    candidates = [
        dict(row.get("candidate") or {})
        for row in raw_ranked
        if isinstance(row.get("candidate"), dict)
    ]

    ranking = rank_real_products(
        candidates,
        real_read.get("quotes_by_product") or {},
        available_capital=available_capital,
        supplier_currency=supplier_currency,
        target_currency=target_currency,
        fx_rates=fx_rates,
    )

    observations = load_observation_history(
        persistence_client,
        limit=history_limit,
    )
    recent_runs = load_recent_runs(
        persistence_client,
        limit=run_limit,
    )
    metrics = build_shadow_metrics(observations)
    metrics_by_key = {
        row.get("product_key"): row
        for row in metrics.get("products") or []
    }

    reviews = []
    qualified_gates = []
    for ranked in ranking.get("ranked") or []:
        key = ranked.get("product_key")
        shadow_metrics = metrics_by_key.get(key) or {
            "product_key": key,
            "observations": 0,
            "observation_days": 0,
            "inventory_confirmation_rate": 0.0,
            "price_stability": {"stable": False},
        }
        review = build_v52_promotion_review(
            ranked,
            shadow_metrics=shadow_metrics,
            observations=observations,
            thresholds=shadow_thresholds,
        )
        reviews.append(review)

        gate = build_v61_real_gate(
            review,
            observations=observations,
            recent_runs=recent_runs,
            persistence_enabled=True,
            provider_handshake=provider_handshake,
        )
        qualified_gates.append(gate)

    queue = build_promotion_queue(reviews)
    ready_gates = [
        row for row in qualified_gates
        if row.get("status") == "real_evidence_human_gate_ready"
    ]

    return {
        "controller_version": "6.2",
        "status": "human_gate_candidate_ready" if ready_gates else "collecting_real_evidence",
        "operation": operation,
        "real_product_ranking": ranking,
        "shadow_metrics": metrics,
        "promotion_queue": queue,
        "real_evidence_gates": qualified_gates,
        "human_gate_ready_count": len(ready_gates),
        "human_gate_ready_product_keys": [
            (row.get("qualification") or {}).get("product_key")
            for row in ready_gates
        ],
        "human_gate_required": True,
        "automatic_execution": False,
        "external_write_enabled": False,
        "live_execution_allowed": False,
    }
