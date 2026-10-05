"""Warashibe GPT Headquarters strategy contracts.

This module only produces strategy state, prioritization, escalation, and review
decisions. It never authorizes or performs real-world commerce.
"""

DEFAULT_PRIORITY_ORDER = [
    "commerce_loop",
    "capital_velocity",
    "learning_loop",
]

CEO_ESCALATION_CATEGORIES = {
    "real_purchase",
    "real_payment",
    "real_listing",
    "real_sale",
    "real_money_movement",
    "secrets_auth_change",
    "destructive_database_change",
    "risky_production_change",
    "north_star_change",
    "human_gate_change",
}


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
    shadow_repository=None,
    maturity_stage="research",
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

    from research_lab.shadow_state import build_validation_snapshot
    validation = build_validation_snapshot(repository=shadow_repository,
                                           maturity_stage=maturity_stage, as_of=observed_at)
    return {
        **validation,
        "status": "headquarters_ready",
        "north_star": north_star,
        "priority_order": list(priority_order),
        "current_state": dict(current_state),
        "current_bottleneck": current_bottleneck,
        "active_strategy": list(active_strategy),
        "human_gate_required": bool(human_gate_required) or validation["human_gate_required"],
        "execution_authorized": False,
        "evidence": dict(evidence),
        "observed_at": observed_at,
    }


def build_ceo_directive(
    *,
    directive_key,
    instruction,
    objective,
    constraints=None,
    issued_at,
):
    if not directive_key or not instruction or not objective or not issued_at:
        raise ValueError("directive_key, instruction, objective, and issued_at are required")
    constraints = constraints or []
    if not isinstance(constraints, list):
        raise ValueError("constraints must be a list")

    return {
        "status": "ceo_directive_received",
        "directive_key": directive_key,
        "instruction": instruction,
        "objective": objective,
        "constraints": list(constraints),
        "issued_at": issued_at,
        "execution_authorized": False,
    }


def prioritize_work_items(items):
    if not isinstance(items, list) or not items:
        raise ValueError("items must be a non-empty list")

    ranked = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("each work item must be a mapping")
        key = item.get("key")
        if not key:
            raise ValueError("each work item requires key")
        if item.get("human_gate_blocked"):
            score = -1
            state = "escalate_to_ceo"
        else:
            impact = int(item.get("north_star_impact", 0))
            bottleneck = int(item.get("bottleneck_relief", 0))
            evidence = int(item.get("evidence_strength", 0))
            readiness = int(item.get("readiness", 0))
            cost = int(item.get("cost", 0))
            score = impact * 4 + bottleneck * 3 + evidence * 2 + readiness - cost
            state = "ranked"

        ranked.append(
            {
                **item,
                "priority_score": score,
                "queue_state": state,
                "execution_authorized": False,
            }
        )

    ranked.sort(key=lambda row: row["priority_score"], reverse=True)
    return {
        "status": "priority_queue_ready",
        "items": ranked,
        "next_item": next(
            (row["key"] for row in ranked if row["queue_state"] == "ranked"),
            None,
        ),
        "execution_authorized": False,
    }


def evaluate_escalation(*, category, requested_action, context=None):
    if not category or not requested_action:
        raise ValueError("category and requested_action are required")
    context = context or {}
    if not isinstance(context, dict):
        raise ValueError("context must be a mapping")

    requires_ceo = category in CEO_ESCALATION_CATEGORIES
    return {
        "status": "ceo_escalation_required" if requires_ceo else "hq_may_prepare",
        "category": category,
        "requested_action": requested_action,
        "requires_ceo": requires_ceo,
        "context": dict(context),
        "execution_authorized": False,
    }


def review_strategy(*, current, evidence, bottleneck_resolved=False, directive_changed=False):
    if not isinstance(current, dict):
        raise ValueError("current must be a mapping")
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be a mapping")

    if directive_changed:
        recommendation = "replan"
        reason = "ceo_directive_changed"
    elif bottleneck_resolved:
        recommendation = "advance"
        reason = "current_bottleneck_resolved"
    else:
        recommendation = "maintain"
        reason = "no_material_strategy_change"

    return {
        "status": "strategy_review_complete",
        "recommendation": recommendation,
        "reason": reason,
        "current_bottleneck": current.get("current_bottleneck"),
        "active_strategy": list(current.get("active_strategy", [])),
        "evidence": dict(evidence),
        "decision_required": recommendation in {"replan", "advance"},
        "execution_authorized": False,
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
