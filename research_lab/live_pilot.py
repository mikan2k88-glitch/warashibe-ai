"""PG-054..056 limited-live readiness and proof-record contracts.

These functions prepare and validate records only. They never purchase, pay, list,
sell, or move money.
"""
from research_lab.evidence_integrity import number

SAFETY = {
    "human_gate_required": True,
    "external_execution_authorized": False,
    "purchase_authorized": False,
}


def evaluate_limited_live_readiness(*, live_readiness, burn_in, candidate_count, max_transactions=1):
    reasons = []
    if live_readiness.get("live_readiness_ready") is not True:
        reasons.append("live_readiness_not_ready")
    if burn_in.get("burn_in_passed") is not True:
        reasons.append("burn_in_not_passed")
    if candidate_count != 1:
        reasons.append("one_item_candidate_required")
    if max_transactions != 1:
        reasons.append("single_transaction_scope_required")
    ready = not reasons
    return {
        "pg": "PG-054",
        "status": "limited_live_review_ready" if ready else "limited_live_blocked",
        "limited_live_review_ready": ready,
        "max_transactions": 1,
        "reasons": reasons,
        **SAFETY,
    }


def build_human_gate_decision_packet(candidate, *, readiness, evidence_pack, max_loss_jpy, decision_deadline):
    reasons = []
    if readiness.get("limited_live_review_ready") is not True:
        reasons.append("readiness_not_satisfied")
    if evidence_pack.get("human_review_ready") is not True:
        reasons.append("evidence_pack_not_ready")
    if not number(max_loss_jpy) or max_loss_jpy <= 0:
        reasons.append("max_loss_not_defined")
    if not isinstance(decision_deadline, str) or not decision_deadline:
        reasons.append("decision_deadline_missing")
    return {
        "pg": "PG-055",
        "status": "human_decision_packet_ready" if not reasons else "human_decision_packet_blocked",
        "candidate_id": candidate.get("candidate_id"),
        "product_identity": candidate.get("product_identity"),
        "source_url": candidate.get("source_url"),
        "expected_net_profit": candidate.get("expected_net_profit"),
        "max_loss_jpy": max_loss_jpy,
        "stop_loss_price": candidate.get("stop_loss_price"),
        "max_hold_days": candidate.get("max_hold_days"),
        "decision_deadline": decision_deadline,
        "reasons": reasons,
        "human_decision_required": True,
        **SAFETY,
    }


def validate_one_item_live_proof(proof):
    """Validate a human-supplied completed-cycle record; never creates the cycle."""
    required = (
        "candidate_id", "purchase_receipt_ref", "inspection_ref", "sale_ref",
        "settlement_ref", "capital_before_jpy", "capital_after_jpy",
    )
    reasons = []
    if not isinstance(proof, dict):
        proof = {}
    for key in required:
        if proof.get(key) in (None, ""):
            reasons.append("missing_" + key)
    before, after = proof.get("capital_before_jpy"), proof.get("capital_after_jpy")
    if not number(before) or not number(after):
        reasons.append("invalid_capital_values")
        delta = None
    else:
        delta = after - before
    if proof.get("human_approved") is not True:
        reasons.append("explicit_human_approval_missing")
    if proof.get("max_transactions") != 1:
        reasons.append("single_transaction_scope_not_proven")
    valid = not reasons
    return {
        "pg": "PG-056",
        "status": "one_item_live_proof_valid" if valid else "one_item_live_proof_invalid",
        "proof_valid": valid,
        "capital_delta_jpy": delta,
        "reasons": reasons,
        "proof_record_only": True,
        **SAFETY,
    }
