from __future__ import annotations

from .actual_evidence_controller import run_actual_evidence_controller
from .v64_gate import assess_v64_promotion_gate


def run_actual_evidence_controller_v64(
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
    base = run_actual_evidence_controller(
        supplier_provider,
        market_provider,
        persistence_client=persistence_client,
        provider_handshake=provider_handshake,
        available_capital=available_capital,
        supplier_currency=supplier_currency,
        target_currency=target_currency,
        fx_rates=fx_rates,
        budget=budget,
        shadow_thresholds=shadow_thresholds,
        history_limit=history_limit,
        run_limit=run_limit,
    )

    if base.get("status") == "setup_required":
        return {
            **base,
            "controller_version": "6.4",
            "cost_terms_gate_ready_count": 0,
        }

    ranked = (base.get("real_product_ranking") or {}).get("ranked") or []
    queue = base.get("promotion_queue") or {}
    reviews = list(queue.get("ready") or []) + list(queue.get("pending") or [])
    review_by_key = {
        str(row.get("product_key") or ""): row
        for row in reviews
    }

    gates = []
    for row in ranked:
        key = str(row.get("product_key") or "")
        review = review_by_key.get(key) or {
            "eligible_for_human_review": False,
            "product_key": key,
        }
        gates.append(assess_v64_promotion_gate(row, review))

    ready = [row for row in gates if row.get("passed") is True]

    return {
        **base,
        "controller_version": "6.4",
        "status": (
            "human_gate_candidate_ready"
            if ready
            else "collecting_cost_and_terms_evidence"
        ),
        "v64_promotion_gates": gates,
        "cost_terms_gate_ready_count": len(ready),
        "cost_terms_gate_ready_product_keys": [
            row.get("product_key") for row in ready
        ],
        "human_gate_ready_count": len(ready),
        "human_gate_ready_product_keys": [
            row.get("product_key") for row in ready
        ],
        "human_gate_required": True,
        "automatic_execution": False,
        "external_write_enabled": False,
        "live_execution_allowed": False,
    }
