"""Bridge real-world candidates into the existing Route Engine.

The bridge adapts real-world candidate fields to the Route Engine schema.
A route ladder may be supplied for future capital states. Without future
market data the bridge fails closed for route probability and reports that
the route is incomplete rather than inventing continuation candidates.
"""

from route_engine import evaluate_route_candidates

REAL_WORLD_ROUTE_BRIDGE_VERSION = "0.1"
DEFAULT_TARGET_JPY = 1_000_000


def adapt_candidate(candidate, scoring=None):
    scoring = scoring or {}
    total_cost = (
        candidate["purchase_price_jpy"]
        + candidate["estimated_fees_jpy"]
        + candidate["estimated_shipping_jpy"]
    )
    return {
        "name": candidate.get("name") or candidate.get("title") or candidate.get("item_id"),
        "item_id": candidate.get("item_id"),
        "purchase_price": total_cost,
        "expected_sale_price": candidate["estimated_sale_price_jpy"],
        "confidence": candidate["confidence"],
        "score": scoring.get("score", 0.0),
        "risk": {
            "risk_level": "bounded",
            "liquidation_value_jpy": candidate.get("liquidation_value_jpy"),
            "maximum_expected_loss_jpy": scoring.get("maximum_expected_loss_jpy"),
            "drawdown_rate": scoring.get("drawdown_rate"),
        },
        "_real_world_candidate": dict(candidate),
    }


def build_route_provider(route_ladder):
    normalized = {}
    for capital, rows in (route_ladder or {}).items():
        normalized[int(capital)] = list(rows)

    def provider(capital):
        return {
            "ranked_candidates": normalized.get(int(capital), []),
        }

    return provider


def evaluate_real_world_routes(
    initial_capital_jpy,
    candidates,
    scoring_by_item_id=None,
    route_ladder=None,
    target_jpy=DEFAULT_TARGET_JPY,
):
    scoring_by_item_id = scoring_by_item_id or {}

    adapted_initial = [
        adapt_candidate(
            candidate,
            scoring_by_item_id.get(candidate.get("item_id"), {}),
        )
        for candidate in candidates
    ]

    ladder = dict(route_ladder or {})
    ladder[int(initial_capital_jpy)] = adapted_initial
    provider = build_route_provider(ladder)

    evaluated = evaluate_route_candidates(
        initial_capital_jpy,
        target_jpy,
        provider,
    )

    has_future_states = any(
        int(capital) != int(initial_capital_jpy)
        and rows
        for capital, rows in ladder.items()
    )

    return {
        "version": REAL_WORLD_ROUTE_BRIDGE_VERSION,
        "target_jpy": target_jpy,
        "route_data_complete": has_future_states,
        "status": "evaluated" if has_future_states else "route_data_incomplete",
        "candidates": tuple(evaluated),
        "network_execution_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
    }
