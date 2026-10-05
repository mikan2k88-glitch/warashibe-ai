"""PG-039 fail-closed promotion to human review, never permission to purchase."""
from research_lab.evidence_integrity import evaluate_integrity, number
from research_lab.product_dd_input_gate import _utc_time


def evaluate_promotion(candidate, *, as_of, max_age_days=7, min_liquidity=0.5, min_net_profit=300):
    candidate = candidate if isinstance(candidate, dict) else {}
    integrity = evaluate_integrity(candidate, as_of=as_of, max_age_days=max_age_days)
    reasons = list(integrity["reasons"])
    if not number(min_liquidity) or min_liquidity > 1 or not number(min_net_profit):
        reasons.append("invalid_promotion_threshold")
    else:
        liquidity = candidate.get("liquidity_score")
        if not number(liquidity) or not min_liquidity <= liquidity <= 1:
            reasons.append("insufficient_liquidity")
        costs = ("acquisition_price", "acquisition_shipping", "acquisition_fees",
                 "expected_selling_fee", "expected_outbound_shipping", "expected_sale_price")
        if not all(number(candidate.get(k)) for k in costs):
            reasons.append("invalid_economics")
        else:
            total = sum(candidate[k] for k in costs[:3])
            profit = candidate["expected_sale_price"] - sum(candidate[k] for k in costs[:5])
            if total <= 0 or profit < min_net_profit:
                reasons.append("net_profit_below_minimum")
            if candidate.get("total_acquisition_cost") != total or candidate.get("expected_net_profit") != profit:
                reasons.append("economics_snapshot_mismatch")
    if candidate.get("maturity_stage") != "shadow":
        reasons.append("shadow_stage_required")
    if candidate.get("condition_risk") != "low":
        reasons.append("condition_risk_unresolved")
    if candidate.get("authenticity_risk") != "low":
        reasons.append("authenticity_risk_unresolved")
    if candidate.get("return_conditions") != "verified":
        reasons.append("return_conditions_unverified")
    if candidate.get("sellability") != "supported":
        reasons.append("sellability_unverified")
    stop = candidate.get("stop_loss_price")
    if not number(stop) or not number(candidate.get("expected_sale_price")) or stop > candidate["expected_sale_price"]:
        reasons.append("stop_loss_not_defined")
    days, hold = candidate.get("estimated_sell_days"), candidate.get("max_hold_days")
    if not number(days, minimum=0.000001) or not number(hold, minimum=0.000001) or days > hold:
        reasons.append("hold_period_not_supported")
    evidence = candidate.get("evidence")
    verified_kinds = {row.get("kind") for row in evidence or [] if isinstance(row, dict)
                      and row.get("evidence_id") in integrity["evidence_refs"] and row.get("assessment") == "verified"} if isinstance(evidence, list) else set()
    for kind in ("authenticity", "condition", "returns", "stop_loss"):
        if kind not in verified_kinds:
            reasons.append("missing_" + kind + "_evidence")
    outcome = candidate.get("outcome") or {}
    now = _utc_time(as_of)
    at = _utc_time(outcome.get("outcome_at")) if isinstance(outcome, dict) else None
    if (candidate.get("status") != "completed" or not isinstance(outcome, dict)
            or outcome.get("outcome_status") != "success" or outcome.get("hypothetical") is not True
            or outcome.get("shadow_candidate_id") != candidate.get("shadow_candidate_id")
            or outcome.get("external_execution_authorized") is not False
            or outcome.get("purchase_authorized") is not False or outcome.get("reasons") != []
            or now is None or at is None or at > now):
        reasons.append("successful_shadow_outcome_required")
    for key in ("external_execution_authorized", "purchase_authorized"):
        if candidate.get(key) is not False:
            reasons.append("execution_boundary_invalid")
    if candidate.get("human_gate_required") is not True:
        reasons.append("human_gate_boundary_invalid")
    reasons = list(dict.fromkeys(reasons))
    ready = not reasons
    return {
        "candidate_id": candidate.get("candidate_id"), "shadow_candidate_id": candidate.get("shadow_candidate_id"),
        "status": "promotion_ready" if ready else "research_usable_not_promotion_ready",
        "promotion_ready": ready, "human_review_ready": ready, "live_ready": False,
        "reasons": reasons, "evidence_integrity_status": integrity["status"],
        "evaluated_at": as_of, "human_gate_required": True,
        "external_execution_authorized": False, "purchase_authorized": False,
    }
