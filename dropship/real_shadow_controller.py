from __future__ import annotations

from .evidence_pack import build_real_read_evidence_pack
from .promotion_review import build_promotion_review_package
from .real_read_runner import run_real_read_research
from .shadow_observation_builder import build_opportunity_observations


def run_real_shadow_controller(
    supplier_provider,
    market_provider,
    *,
    historical_observations: list[dict] | None = None,
    supplier_currency: str = "USD",
    target_currency: str | None = None,
    fx_rates: dict | None = None,
    budget: dict | None = None,
    shadow_thresholds: dict | None = None,
    mode: str = "real_read",
) -> dict:
    real_read = run_real_read_research(
        supplier_provider,
        market_provider,
        supplier_currency=supplier_currency,
        target_currency=target_currency,
        fx_rates=fx_rates,
        budget=budget,
    )
    current_observations = build_opportunity_observations(real_read)
    all_observations = list(historical_observations or []) + current_observations
    evidence = build_real_read_evidence_pack(
        real_read,
        all_observations,
        mode=mode,
        thresholds=shadow_thresholds,
    )

    ranked_by_key = {
        row.get("product_key"): row
        for row in (real_read.get("ranking") or {}).get("ranked") or []
    }
    reviews = []
    for gate_row in evidence["product_gates"]:
        key = gate_row["product_key"]
        opportunity = ranked_by_key.get(key)
        if not opportunity:
            continue
        metrics = gate_row["metrics"]
        reviews.append(build_promotion_review_package(
            opportunity,
            gate_row["gate"],
            observation_count=metrics.get("observations", 0),
            observation_days=metrics.get("observation_days", 0),
        ))

    ready = [row for row in reviews if row["eligible_for_human_review"]]
    return {
        "status": "promotion_review_ready" if ready else "shadow_collecting",
        "real_read": real_read,
        "current_observations": current_observations,
        "all_observation_count": len(all_observations),
        "evidence": evidence,
        "promotion_reviews": reviews,
        "ready_product_keys": [row["product_key"] for row in ready],
        "commerce_external_writes": False,
        "automatic_promotion": False,
        "live_execution_allowed": False,
    }
