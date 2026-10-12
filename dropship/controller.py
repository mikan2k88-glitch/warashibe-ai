from __future__ import annotations

from .commerce import build_sandbox_commerce_plan
from .promotion import assess_promotion
from .ranking import rank_supplier_offers
from .selection import select_single_candidate
from .shadow import evaluate_shadow_candidate


def run_controller(
    offers: list[dict],
    *,
    strategy: str = "balanced",
    available_capital: float = 3000.0,
) -> dict:
    ranking = rank_supplier_offers(offers)
    selection = select_single_candidate(
        ranking,
        strategy=strategy,
        available_capital=available_capital,
    )
    selected = selection.get("selected")
    if not selected:
        return {
            "status": "blocked",
            "stage": "selection",
            "ranking": ranking,
            "selection": selection,
            "external_writes": False,
            "live_execution_allowed": False,
        }

    selected_input = dict(selected.get("input") or {})
    shadow = evaluate_shadow_candidate(selected_input)
    promotion = assess_promotion(shadow)
    if not promotion["promotion_ready"]:
        return {
            "status": "collecting",
            "stage": "shadow",
            "ranking": ranking,
            "selection": selection,
            "shadow": shadow,
            "promotion": promotion,
            "external_writes": False,
            "live_execution_allowed": False,
        }

    commerce = build_sandbox_commerce_plan([selected_input])
    return {
        "status": "completed" if commerce.get("status") == "completed" else "blocked",
        "stage": "sandbox_settlement" if commerce.get("status") == "completed" else "sandbox",
        "strategy": strategy,
        "available_capital": float(available_capital),
        "ranking": ranking,
        "selection": selection,
        "shadow": shadow,
        "promotion": promotion,
        "commerce": commerce,
        "selected_product_key": selected["offer"]["product_key"],
        "expected_net_profit": selected["economics"]["net_profit"],
        "required_working_capital": selected["economics"]["required_working_capital"],
        "external_writes": False,
        "live_execution_allowed": False,
        "human_gate_required_for_live": True,
    }
