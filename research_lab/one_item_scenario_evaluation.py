"""Read-only, single-item fixture evaluation with explicit cost and loss assumptions."""

from math import isfinite

from research_lab.market_decision_virtual_trade import simulate_decision_trade
from research_lab.virtual_trade_costs import apply_virtual_trade_costs


def evaluate_one_item_scenario(decision: dict, *, cost_kwargs: dict | None = None) -> dict:
    """Compare hypothetical win and loss without a draw, trade, or external call."""
    if not isinstance(decision, dict):
        raise ValueError("decision must be a dictionary")
    if cost_kwargs is not None and (not isinstance(cost_kwargs, dict) or
                                    set(cost_kwargs) - {"inbound_shipping", "outbound_shipping", "selling_fee_rate"}):
        raise ValueError("unsupported cost settings")
    candidate = decision.get("best_candidate")
    # Reuse the existing transition and ledger validators for both outcomes.
    success = simulate_decision_trade(decision, 0.0)
    if candidate is None:
        return {"selected_item": None, "selection_reason": "no_quality_gated_candidate",
                "capital_before": success["capital_before"],
                "expected_net_profit": None, "failure_probability": None,
                "failure_capital": None, "hypothetical_costs": None,
                "one_item_only": True, "scenario_only": True,
                "external_action_authorized": False}
    probability = candidate["confidence"]
    if isinstance(probability, bool) or not isinstance(probability, (int, float)) or not isfinite(probability) or not 0 <= probability <= 1:
        raise ValueError("invalid confidence")
    # 0.0 is not necessarily a success if confidence=0; derive both
    # hypothetical branches explicitly from a validated copy.
    winning = dict(decision, best_candidate={**candidate, "confidence": 1.0})
    losing = dict(decision, best_candidate={**candidate, "confidence": 0.0})
    win = simulate_decision_trade(winning, 0.0)
    loss = simulate_decision_trade(losing, 0.0)
    if cost_kwargs is not None:
        win = apply_virtual_trade_costs(win, **cost_kwargs)
        loss = apply_virtual_trade_costs(loss, **cost_kwargs)
    capital = win["capital_before"]
    return {
        "selected_item": win["selected_item"],
        "selection_reason": "existing_quality_gated_best_candidate",
        "capital_before": capital,
        "purchase_price": win["purchase_price"],
        "assumed_sale_probability": probability,
        "failure_probability": 1 - probability,
        "success_capital": win["capital_after"],
        "failure_capital": loss["capital_after"],
        "success_net_profit": win["capital_after"] - capital,
        "failure_net_profit": loss["capital_after"] - capital,
        "expected_net_profit": (probability * win["capital_after"]
                                + (1 - probability) * loss["capital_after"] - capital),
        "hypothetical_costs": {"success": win.get("total_costs", 0),
                               "failure": loss.get("total_costs", 0)},
        "cost_model": "cash_ledger" if cost_kwargs is not None else "legacy_gross",
        "one_item_only": True, "scenario_only": True,
        "external_action_authorized": False,
    }
