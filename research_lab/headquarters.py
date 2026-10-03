"""Warashibe GPT Headquarters strategy contracts.

This module only produces strategy state and transition decisions.
It never authorizes or performs real-world commerce.
"""

DEFAULT_PRIORITY_ORDER = [
    "commerce_loop",
    "capital_velocity",
    "learning_loop",
]


def build_headquarters_snapshot(
    *,
    north_star,
    priority_order,
    current_state,
    current_bottleneck,
    active_strategy,
    human_gate_required,
    evidence,
    observed_at,
):
    required = {
        "north_star": north_star,
        "current_bottleneck": current_bottleneck,
        "observed_at": observed_at,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ValueError(f"missing headquarters fields: {', '.join(missing)}")
    if not isinstance(priority_order, list) or not priority_order:
        raise ValueError("priority_order must be a non-empty list")
    if not isinstance(active_strategy, list) or not active_strategy:
        raise ValueError("active_strategy must be a non-empty list")
    if not isinstance(current_state, dict):
        raise ValueError("current_state must be a mapping")
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be a mapping")

    return {
        "status": "headquarters_ready",
        "north_star": north_star,
        "priority_order": list(priority_order),
        "current_state": dict(current_state),
        "current_bottleneck": current_bottleneck,
        "active_strategy": list(active_strategy),
        "human_gate_required": bool(human_gate_required),
        "execution_authorized": False,
        "evidence": dict(evidence),
        "observed_at": observed_at,
    }


def evaluate_strategy_transition(current, candidate, evidence):
    if not isinstance(current, dict):
        raise ValueError("current strategy snapshot must be a mapping")
    if not isinstance(candidate, dict):
        raise ValueError("candidate strategy must be a mapping")
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be a mapping")

    candidate_bottleneck = candidate.get(
        "current_bottleneck", current.get("current_bottleneck")
    )
    candidate_strategy = candidate.get(
        "active_strategy", current.get("active_strategy", [])
    )

    material_change = (
        candidate_bottleneck != current.get("current_bottleneck")
        or list(candidate_strategy) != list(current.get("active_strategy", []))
    )

    return {
        "status": (
            "strategy_transition_proposed"
            if material_change
            else "strategy_unchanged"
        ),
        "material_change": material_change,
        "decision_required": material_change,
        "current_bottleneck": current.get("current_bottleneck"),
        "candidate_bottleneck": candidate_bottleneck,
        "current_strategy": list(current.get("active_strategy", [])),
        "candidate_strategy": list(candidate_strategy),
        "evidence": dict(evidence),
        "human_gate_required": True,
        "execution_authorized": False,
    }
