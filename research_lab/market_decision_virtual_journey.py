"""Bounded offline journey using the existing market decision and virtual trade.

The injected provider_factory supplies fixture evidence for each step. This
module performs no external actions and never splits capital across items.
"""

from math import isfinite

from research_lab.end_to_end_market_decision_pipeline import run_market_decision
from research_lab.market_decision_virtual_trade import simulate_decision_trade
from research_lab.virtual_trade_costs import apply_virtual_trade_costs

VIRTUAL_JOURNEY_VERSION = "0.1"


def run_virtual_journey(provider_factory, query: str, start_capital: float,
                        draws: tuple[float, ...], target: float = 1_000_000,
                        max_steps: int = 20, salvage_on_failure: bool = False,
                        cost_kwargs: dict | None = None, **gate_kwargs) -> dict:
    """Run at most max_steps; supplied draws make outcomes reproducible."""
    if cost_kwargs is not None and (not isinstance(cost_kwargs, dict) or
                                    set(cost_kwargs) - {"inbound_shipping", "outbound_shipping", "selling_fee_rate"}):
        raise ValueError("cost_kwargs must contain only supported cost fields")
    if not isinstance(salvage_on_failure, bool):
        raise ValueError("salvage_on_failure must be boolean")
    for key, value in (("start_capital", start_capital), ("target", target)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value <= 0:
            raise ValueError(f"{key} must be finite and positive")
    if isinstance(max_steps, bool) or not isinstance(max_steps, int) or not 1 <= max_steps <= 20:
        raise ValueError("max_steps must be an integer from 1 to 20")
    if not isinstance(draws, tuple) or len(draws) < max_steps:
        raise ValueError("draws must provide at least max_steps values")
    if not callable(provider_factory):
        raise ValueError("provider_factory must be callable")
    # Validate all draws before fetching any evidence.
    for draw in draws[:max_steps]:
        if isinstance(draw, bool) or not isinstance(draw, (int, float)) or not isfinite(draw) or not 0 <= draw < 1:
            raise ValueError("draw must be in [0, 1)")

    capital = start_capital
    history = []
    status = "max_steps_reached" if capital < target else "goal_reached"
    if capital < target:
        for step in range(1, max_steps + 1):
            provider = provider_factory(step, capital)
            decision_run = run_market_decision(provider, query, capital, **gate_kwargs)
            trade = simulate_decision_trade(decision_run.decision, draws[step - 1],
                                            salvage_on_failure=salvage_on_failure)
            if cost_kwargs is not None:
                trade = apply_virtual_trade_costs(trade, **cost_kwargs)
            history.append({"step": step, **trade})
            capital = trade["capital_after"]
            if trade["status"] == "no_candidate":
                status = "no_candidate"
                break
            if trade["status"] == "failed":
                status = "failed"
                break
            if capital >= target:
                status = "goal_reached"
                break
    return {"version": VIRTUAL_JOURNEY_VERSION, "status": status,
            "start_capital": start_capital, "target": target,
            "final_capital": capital, "steps": len(history),
            "history": history, "external_action_authorized": False}
