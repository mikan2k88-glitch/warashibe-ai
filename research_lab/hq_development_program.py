"""HQ P1-P7 development program.

This module implements the development/control capabilities for the formal HQ
priority queue. It prepares and evaluates strategy artifacts only. It never
performs purchase, payment, listing, sale, money movement, or other Human Gate
actions.
"""

PRIORITIES = [
    ("P1", "hq_runner_integration"),
    ("P2", "real_pilot_readiness"),
    ("P3", "ceo_approval_gate"),
    ("P4", "one_item_live_proof"),
    ("P5", "learning_feedback"),
    ("P6", "capital_velocity_improvement"),
    ("P7", "controlled_automation_expansion"),
]

_OPERATIONAL_KEYS = {
    "P1": "hq_runner_integrated",
    "P2": "real_pilot_decision_packet_ready",
    "P3": "ceo_approval_gate_ready",
    "P4": "live_pilot_verified",
    "P5": "learning_feedback_ingested",
    "P6": "capital_velocity_optimized",
    "P7": "controlled_automation_scope_ready",
}

SAFE_AUTOMATABLE_SCOPES = [
    "candidate_research",
    "evidence_collection",
    "economics_evaluation",
    "priority_ranking",
    "runtime_verification",
    "learning_feedback_preparation",
]

HUMAN_GATE_SCOPES = [
    "real_purchase",
    "real_payment",
    "real_listing",
    "real_sale",
    "real_money_movement",
    "secrets_auth_change",
]


def _mapping(value, name):
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a mapping")
    return value


def _money(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{name} must be a non-negative number")
    return int(round(value))


def _positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{name} must be a positive number")
    return float(value)


def build_hq_development_program(*, operational_evidence=None):
    evidence = dict(operational_evidence or {})
    progress = []
    selected = None
    for code, objective in PRIORITIES:
        completed = evidence.get(_OPERATIONAL_KEYS[code]) is True
        progress.append(
            {
                "priority": code,
                "objective": objective,
                "operationally_completed": completed,
            }
        )
        if selected is None and not completed:
            selected = code

    return {
        "status": "hq_development_program_ready",
        "development_endpoint": "P7",
        "development_capabilities": [code for code, _ in PRIORITIES],
        "all_development_capabilities_implemented": True,
        "operational_progress": progress,
        "selected_operational_priority": selected,
        "human_gate_preserved": True,
        "external_execution_authorized": False,
    }


def build_real_pilot_decision_packet(*, candidate, economics, readiness):
    candidate = _mapping(candidate, "candidate")
    economics = _mapping(economics, "economics")
    readiness = _mapping(readiness, "readiness")

    if economics.get("status") != "economics_ready":
        raise ValueError("economics_ready required")
    if (economics.get("profit_gate") or {}).get("economically_viable") is not True:
        raise ValueError("economically viable economics required")
    if readiness.get("status") != "live_readiness_audit_complete":
        raise ValueError("live_readiness_audit_complete required")
    if readiness.get("ready_for_human_go_no_go") is not True:
        raise ValueError("readiness must be ready for human review")
    if readiness.get("human_go_no_go_required") is not True:
        raise ValueError("human go/no-go must remain required")
    if readiness.get("live_commerce_authorized") is not False:
        raise ValueError("live commerce must remain unauthorized")

    purchase = _money(candidate.get("purchase_price_jpy"), "purchase_price_jpy")
    expected_sale = _money(
        candidate.get("expected_sale_price_jpy"), "expected_sale_price_jpy"
    )
    max_loss = _money(economics.get("max_loss_jpy"), "max_loss_jpy")
    max_hold_days = int(_positive(economics.get("max_hold_days"), "max_hold_days"))

    return {
        "status": "real_pilot_decision_packet_ready",
        "item_key": candidate.get("item_key"),
        "provider": candidate.get("provider"),
        "quantity": 1,
        "purchase_price_jpy": purchase,
        "expected_sale_price_jpy": expected_sale,
        "expected_net_profit_jpy": economics.get("expected_net_profit_jpy"),
        "expected_margin_rate": economics.get("expected_margin_rate"),
        "liquidity_score": candidate.get("liquidity_score"),
        "condition_risk": candidate.get("condition_risk"),
        "authenticity_risk": candidate.get("authenticity_risk"),
        "max_loss_jpy": max_loss,
        "stop_loss_price_jpy": economics.get("stop_loss_price_jpy"),
        "max_hold_days": max_hold_days,
        "human_gate_required": True,
        "purchase_authorized": False,
        "payment_authorized": False,
        "sale_authorized": False,
        "external_execution_authorized": False,
    }


def build_ceo_approval_packet(decision_packet):
    packet = _mapping(decision_packet, "decision_packet")
    if packet.get("status") != "real_pilot_decision_packet_ready":
        raise ValueError("real_pilot_decision_packet_ready required")
    return {
        "status": "ceo_approval_gate_ready",
        "item_key": packet.get("item_key"),
        "provider": packet.get("provider"),
        "quantity": 1,
        "why_this_item": {
            "expected_net_profit_jpy": packet.get("expected_net_profit_jpy"),
            "expected_margin_rate": packet.get("expected_margin_rate"),
            "liquidity_score": packet.get("liquidity_score"),
        },
        "maximum_loss_jpy": packet.get("max_loss_jpy"),
        "maximum_capital_lock_days": packet.get("max_hold_days"),
        "abort_conditions": {
            "stop_loss_price_jpy": packet.get("stop_loss_price_jpy"),
            "max_hold_days": packet.get("max_hold_days"),
        },
        "human_gate_required": True,
        "explicit_ceo_approval_required": True,
        "execution_authorized": False,
    }


def build_live_pilot_execution_plan(approval_packet, human_approval=None):
    packet = _mapping(approval_packet, "approval_packet")
    if packet.get("status") != "ceo_approval_gate_ready":
        raise ValueError("ceo_approval_gate_ready required")

    if human_approval is None:
        return {
            "status": "live_pilot_waiting_for_ceo",
            "item_key": packet.get("item_key"),
            "human_gate_required": True,
            "execution_authorized": False,
            "external_execution_authorized": False,
        }

    approval = _mapping(human_approval, "human_approval")
    if str(approval.get("decision") or "").lower() != "approve":
        return {
            "status": "live_pilot_not_approved",
            "item_key": packet.get("item_key"),
            "human_gate_required": True,
            "execution_authorized": False,
            "external_execution_authorized": False,
        }
    if not approval.get("approval_key"):
        raise ValueError("approval_key required")
    budget = _money(approval.get("approved_budget_jpy"), "approved_budget_jpy")
    if budget <= 0:
        raise ValueError("positive approved budget required")

    return {
        "status": "bounded_live_pilot_ready",
        "item_key": packet.get("item_key"),
        "quantity": 1,
        "approval_key": approval.get("approval_key"),
        "approved_budget_jpy": budget,
        "required_chain": [
            "single_purchase_execution",
            "purchase_receipt_reconciliation",
            "receive_inspection",
            "human_sale_decision",
            "limited_sale_execution",
            "trade_settlement",
            "one_cycle_warashibe_proof",
        ],
        "human_gate_preserved": True,
        "external_execution_authorized": False,
        "execution_authorized": False,
    }


def build_learning_feedback(review):
    review = _mapping(review, "review")
    if review.get("status") != "live_pilot_review_complete":
        raise ValueError("live_pilot_review_complete required")
    actual = _mapping(review.get("actual"), "review.actual")
    errors = _mapping(review.get("prediction_error"), "review.prediction_error")
    return {
        "status": "learning_feedback_ready",
        "review_key": review.get("review_key"),
        "item_key": review.get("item_key"),
        "live_verified": review.get("live_pilot_verified") is True,
        "actual": dict(actual),
        "prediction_error": dict(errors),
        "next_capital_jpy": actual.get("next_capital_jpy"),
        "ranking_feedback_ready": True,
        "external_execution_authorized": False,
    }


def rank_capital_velocity_candidates(candidates):
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("candidates must be a non-empty list")

    ranked = []
    for candidate in candidates:
        row = _mapping(candidate, "candidate")
        profit = float(_money(row.get("expected_profit_jpy"), "expected_profit_jpy"))
        days = _positive(row.get("estimated_days_to_sell"), "estimated_days_to_sell")
        confidence = row.get("confidence", 1.0)
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        confidence = max(0.0, min(1.0, float(confidence)))
        velocity = profit / days
        score = velocity * confidence
        ranked.append(
            {
                **row,
                "expected_capital_velocity_jpy_per_day": round(velocity, 2),
                "velocity_confidence_score": round(score, 2),
            }
        )

    ranked.sort(key=lambda row: row["velocity_confidence_score"], reverse=True)
    return {
        "status": "capital_velocity_ranking_ready",
        "ranked_candidates": ranked,
        "best_candidate": ranked[0],
        "external_execution_authorized": False,
    }


def evaluate_controlled_automation_scope(reviews, *, min_live_cycles=3):
    if not isinstance(reviews, list):
        raise ValueError("reviews must be a list")
    if isinstance(min_live_cycles, bool) or not isinstance(min_live_cycles, int) or min_live_cycles < 1:
        raise ValueError("min_live_cycles must be a positive integer")

    verified = sum(
        1
        for review in reviews
        if isinstance(review, dict)
        and review.get("status") == "live_pilot_review_complete"
        and review.get("live_pilot_verified") is True
    )
    eligible = verified >= min_live_cycles

    return {
        "status": "controlled_automation_scope_ready",
        "verified_live_cycles": verified,
        "minimum_verified_live_cycles": min_live_cycles,
        "eligible_for_safe_scope_expansion": eligible,
        "proposed_automatable_scopes": list(SAFE_AUTOMATABLE_SCOPES) if eligible else [],
        "human_gate_scopes": list(HUMAN_GATE_SCOPES),
        "human_gate_preserved": True,
        "automation_authorized": False,
        "external_execution_authorized": False,
    }
