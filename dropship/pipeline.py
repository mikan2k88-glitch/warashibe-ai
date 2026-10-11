from __future__ import annotations

from .commerce import build_sandbox_commerce_plan
from .promotion import assess_promotion
from .ranking import rank_supplier_offers
from .shadow import evaluate_shadow_candidate


def run_dropship_decision_pipeline(offers: list[dict]) -> dict:
    ranking = rank_supplier_offers(offers)
    best = ranking.get("best")
    if not best:
        return {
            "status": "blocked",
            "stage": "supplier_ranking",
            "reason": "no_eligible_offer",
            "ranking": ranking,
            "external_writes": False,
            "live_execution_allowed": False,
        }

    shadow = evaluate_shadow_candidate(best.get("input") or {})
    promotion = assess_promotion(shadow)
    if not promotion["promotion_ready"]:
        return {
            "status": "collecting",
            "stage": "shadow",
            "ranking": ranking,
            "shadow": shadow,
            "promotion": promotion,
            "external_writes": False,
            "live_execution_allowed": False,
        }

    commerce = build_sandbox_commerce_plan(offers)
    return {
        "status": "completed" if commerce.get("status") == "completed" else "blocked",
        "stage": "sandbox_settlement" if commerce.get("status") == "completed" else "sandbox",
        "ranking": ranking,
        "shadow": shadow,
        "promotion": promotion,
        "commerce": commerce,
        "selected_product_key": best["offer"]["product_key"],
        "expected_net_profit": best["economics"]["net_profit"],
        "external_writes": False,
        "live_execution_allowed": False,
        "human_gate_required_for_live": True,
    }
