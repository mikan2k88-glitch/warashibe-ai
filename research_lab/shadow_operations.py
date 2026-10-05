"""PG-043..046 prospective Shadow operation contracts.

No network request, purchase, listing, payment, or sale is performed here. Market
data must be supplied by a read-only adapter and is treated as untrusted input.
"""
from datetime import timedelta

from research_lab.evidence_gate_v2 import evaluate_evidence_integrity_v2
from research_lab.evidence_integrity import number, same_identity
from research_lab.product_dd_input_gate import _utc_time

SAFETY = {
    "human_gate_required": True,
    "external_execution_authorized": False,
    "purchase_authorized": False,
}


def schedule_shadow_reobservation(
    shadow_candidate,
    *,
    as_of,
    interval_hours=24,
    attempt=0,
    max_attempts=7,
):
    now = _utc_time(as_of)
    if now is None:
        raise ValueError("valid as_of required")
    if (
        isinstance(interval_hours, bool)
        or not isinstance(interval_hours, (int, float))
        or interval_hours <= 0
        or isinstance(attempt, bool)
        or not isinstance(attempt, int)
        or attempt < 0
        or isinstance(max_attempts, bool)
        or not isinstance(max_attempts, int)
        or max_attempts < 1
    ):
        raise ValueError("invalid schedule")
    exhausted = attempt >= max_attempts
    return {
        "pg": "PG-043",
        "shadow_candidate_id": shadow_candidate.get("shadow_candidate_id"),
        "status": "exhausted" if exhausted else "scheduled",
        "attempt": attempt,
        "max_attempts": max_attempts,
        "next_observation_at": None if exhausted else (now + timedelta(hours=interval_hours)).isoformat(),
        **SAFETY,
    }


def normalize_market_observation(candidate, raw, *, observed_at):
    """PG-044 adapter boundary: normalize a read-only market observation."""
    if not isinstance(candidate, dict) or not isinstance(raw, dict):
        raise ValueError("candidate/raw mapping required")
    when = _utc_time(observed_at)
    if when is None:
        raise ValueError("valid observed_at required")
    identity = raw.get("product_identity")
    if not same_identity(candidate.get("product_identity"), identity):
        raise ValueError("product identity mismatch")
    stock = raw.get("stock_status")
    if stock not in {"available", "unavailable", "sold_out"}:
        raise ValueError("invalid stock status")
    numeric = ("source_price", "market_price", "liquidity_score")
    if any(not number(raw.get(k)) for k in numeric):
        raise ValueError("invalid numeric observation")
    if raw["liquidity_score"] > 1:
        raise ValueError("liquidity out of range")
    evidence = raw.get("evidence")
    if not isinstance(evidence, list):
        raise ValueError("evidence list required")
    return {
        "pg": "PG-044",
        "shadow_candidate_id": candidate.get("shadow_candidate_id"),
        "product_identity": identity,
        "observed_at": when.isoformat(),
        "stock_status": stock,
        "source_price": raw["source_price"],
        "market_price": raw["market_price"],
        "liquidity_score": raw["liquidity_score"],
        "active_listing_count": int(raw.get("active_listing_count", 0)),
        "sold_evidence_count": int(raw.get("sold_evidence_count", 0)),
        "estimated_sale_price": raw.get("estimated_sale_price", raw["market_price"]),
        "expected_selling_fee": raw.get("expected_selling_fee", candidate.get("expected_selling_fee")),
        "expected_outbound_shipping": raw.get("expected_outbound_shipping", candidate.get("expected_outbound_shipping")),
        "condition_changes": raw.get("condition_changes", False),
        "evidence": evidence,
        "read_only_adapter": True,
        **SAFETY,
    }


def compute_shadow_outcome(candidate, observations, *, as_of):
    """PG-045 conservative hypothetical result from persisted observations."""
    now = _utc_time(as_of)
    if now is None or not isinstance(observations, list) or not observations:
        raise ValueError("valid observations and clock required")
    latest = observations[-1]
    acquired = candidate.get("total_acquisition_cost")
    sale = latest.get("estimated_sale_price")
    fee = latest.get("expected_selling_fee")
    outbound = latest.get("expected_outbound_shipping")
    reasons = []
    if not all(number(v) for v in (acquired, sale, fee, outbound)):
        reasons.append("invalid_economics")
        profit = None
    else:
        profit = sale - fee - outbound - acquired
    if latest.get("stock_status") != "available":
        reasons.append("source_not_available")
    if latest.get("liquidity_score", 0) < 0.5:
        reasons.append("low_liquidity")
    expected = candidate.get("expected_net_profit")
    variance = None if profit is None or not number(expected) else profit - expected
    return {
        "pg": "PG-045",
        "shadow_candidate_id": candidate.get("shadow_candidate_id"),
        "status": "success" if not reasons and profit is not None and profit >= 300 else "reject",
        "hypothetical": True,
        "hypothetical_net_profit": profit,
        "forecast_variance": variance,
        "observation_count": len(observations),
        "outcome_at": now.isoformat(),
        "reasons": reasons + ([] if profit is None or profit >= 300 else ["net_profit_below_minimum"]),
        **SAFETY,
    }


def build_promotion_evidence_pack(candidate, promotion_result, *, as_of):
    """PG-046 immutable-ish CEO review payload; still not a purchase permission."""
    integrity = evaluate_evidence_integrity_v2(candidate, as_of=as_of)
    ready = (
        isinstance(promotion_result, dict)
        and promotion_result.get("promotion_ready") is True
        and integrity["passed"] is True
    )
    return {
        "pg": "PG-046",
        "status": "human_review_packet_ready" if ready else "packet_blocked",
        "candidate_id": candidate.get("candidate_id"),
        "shadow_candidate_id": candidate.get("shadow_candidate_id"),
        "product_identity": candidate.get("product_identity"),
        "source_url": candidate.get("source_url"),
        "economics": {
            "total_acquisition_cost": candidate.get("total_acquisition_cost"),
            "expected_sale_price": candidate.get("expected_sale_price"),
            "expected_net_profit": candidate.get("expected_net_profit"),
            "stop_loss_price": candidate.get("stop_loss_price"),
            "max_hold_days": candidate.get("max_hold_days"),
        },
        "promotion": promotion_result,
        "evidence_integrity": integrity,
        "human_review_ready": ready,
        **SAFETY,
    }
