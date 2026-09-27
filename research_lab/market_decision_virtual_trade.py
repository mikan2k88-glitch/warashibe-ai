"""Offline one-item transition from a quality-gated market decision.

This is a gross-sale simulation consistent with simulation_engine's current
candidate-cycle convention. No purchase, account, or external state is changed.
"""

from math import isfinite

VIRTUAL_TRADE_VERSION = "0.1"


def simulate_decision_trade(decision: dict, draw: float, *, salvage_on_failure: bool = False) -> dict:
    """Apply one supplied random draw to one proposed candidate, fail closed."""
    if not isinstance(salvage_on_failure, bool):
        raise ValueError("salvage_on_failure must be boolean")
    capital = decision["current_capital"]
    if isinstance(capital, bool) or not isinstance(capital, (int, float)) or not isfinite(capital) or capital < 0:
        raise ValueError("current_capital must be finite and nonnegative")
    if isinstance(draw, bool) or not isinstance(draw, (int, float)) or not isfinite(draw) or not 0 <= draw < 1:
        raise ValueError("draw must be in [0, 1)")
    candidate = decision.get("best_candidate")
    if candidate is None:
        return {"version": VIRTUAL_TRADE_VERSION, "status": "no_candidate",
                "capital_before": capital, "capital_after": capital, "selected_item": None}
    if not isinstance(candidate, dict):
        raise ValueError("best_candidate must be a dictionary")
    price = candidate.get("purchase_price")
    sale = candidate.get("expected_sale_price")
    probability = candidate.get("confidence")
    for key, value in (("purchase_price", price), ("expected_sale_price", sale), ("confidence", probability)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
            raise ValueError(f"{key} must be finite")
    if not 0 < price <= capital or sale < 0 or not 0 <= probability <= 1:
        raise ValueError("candidate trade values are outside allowed bounds")
    success = draw < probability
    recovery = 0
    if not success and salvage_on_failure:
        metadata = candidate.get("metadata")
        if not isinstance(metadata, dict):
            raise ValueError("salvage requires candidate metadata")
        recovery = metadata.get("recovery_value")
        if (isinstance(recovery, bool) or not isinstance(recovery, (int, float))
                or not isfinite(recovery) or not 0 <= recovery <= capital):
            raise ValueError("recovery_value must be finite and within available capital")
    status = "success" if success else ("salvaged" if recovery > 0 else "failed")
    return {"version": VIRTUAL_TRADE_VERSION, "status": status,
            "capital_before": capital, "capital_after": sale if success else recovery,
            "selected_item": candidate["name"], "purchase_price": price,
            "gross_sale_value": sale, "sale_probability": probability,
            "draw": draw, "success": success, "salvage_on_failure": salvage_on_failure, "external_action_authorized": False}
