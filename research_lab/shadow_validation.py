"""PG-038 frozen candidates, later observations and hypothetical outcomes only."""
from copy import deepcopy
from uuid import uuid4

from research_lab.evidence_integrity import evaluate_integrity, evaluate_observation, observation_evaluation, number, same_identity
from research_lab.maturity_stage import require_operation
from research_lab.product_dd_input_gate import _utc_time

SAFETY = {"external_execution_authorized": False, "purchase_authorized": False,
          "human_gate_required": True}
_ASSESSMENT_FIELDS = (
    "candidate_id", "product_identity", "source_url", "observed_at", "acquisition_shipping",
    "acquisition_fees", "expected_selling_fee", "expected_outbound_shipping", "evidence", "strategy",
    "condition_risk", "authenticity_risk", "return_conditions", "sellability", "stop_loss_price", "max_hold_days",
)


def _clock(value):
    time = _utc_time(value)
    if time is None:
        raise ValueError("timezone-aware observation clock required")
    return time


def _no_authority(record):
    if any(key.endswith("authorized") and value is not False for key, value in record.items()):
        raise ValueError("shadow cannot carry execution authority")


def create_shadow_candidate(candidate, assessment, *, repository, as_of, maturity_stage="shadow"):
    require_operation(maturity_stage, "shadow_candidate_save")
    now = _clock(as_of)
    if not isinstance(candidate, dict) or not isinstance(assessment, dict):
        raise ValueError("candidate and assessment must be mappings")
    _no_authority(candidate)
    _no_authority(assessment)
    metadata = candidate.get("metadata") or {}
    for existing in (candidate, metadata):
        if not isinstance(existing, dict):
            raise ValueError("candidate metadata must be a mapping")
        if existing.get("candidate_id") and existing["candidate_id"] != assessment.get("candidate_id"):
            raise ValueError("candidate identifier mismatch")
        if existing.get("product_identity") and not same_identity(existing["product_identity"], assessment.get("product_identity")):
            raise ValueError("candidate product identity mismatch")
        if existing.get("product_id") and existing["product_id"] != (assessment.get("product_identity") or {}).get("product_id"):
            raise ValueError("candidate product ID mismatch")
    evaluation = candidate.get("evaluation") or {}
    if not isinstance(evaluation, dict):
        raise ValueError("candidate evaluation must be a mapping")
    row = {key: deepcopy(assessment.get(key)) for key in _ASSESSMENT_FIELDS}
    row.update({"shadow_candidate_id": str(uuid4()), "product_name": candidate.get("name"),
                "category": candidate.get("category"), "source": candidate.get("source"),
                "acquisition_price": candidate.get("purchase_price"),
                "expected_sale_price": candidate.get("expected_sale_price"),
                "liquidity_score": evaluation.get("liquidity_score"),
                "estimated_sell_days": evaluation.get("estimated_days_to_sell"),
                "maturity_stage": "shadow", "status": "active", "created_at": now.isoformat(), **SAFETY})
    if not isinstance(row["candidate_id"], str) or not row["candidate_id"].strip():
        raise ValueError("candidate_id required to freeze candidate")
    if not isinstance(row["product_name"], str) or not row["product_name"].strip():
        raise ValueError("product name required")
    observed = _clock(row["observed_at"])
    if observed > now:
        raise ValueError("future candidate observation")
    costs = ("acquisition_price", "acquisition_shipping", "acquisition_fees",
             "expected_sale_price", "expected_selling_fee", "expected_outbound_shipping")
    if any(not number(row[k]) for k in costs) or row["acquisition_price"] <= 0:
        raise ValueError("finite nonnegative costs and positive acquisition price required")
    row["total_acquisition_cost"] = sum(row[k] for k in costs[:3])
    row["expected_net_profit"] = (row["expected_sale_price"] - row["expected_selling_fee"]
                                  - row["expected_outbound_shipping"] - row["total_acquisition_cost"])
    if not number(row["total_acquisition_cost"], minimum=0.000001) or not number(abs(row["expected_net_profit"])):
        raise ValueError("derived economics must be finite")
    row["expected_roi"] = row["expected_net_profit"] / row["total_acquisition_cost"]
    identity = row["product_identity"] if isinstance(row["product_identity"], dict) else {}
    for key in ("condition", "edition", "included_items"):
        row[key] = deepcopy(identity.get(key))
    integrity = evaluate_integrity(row, as_of=as_of)
    row["evidence_refs"] = integrity["evidence_refs"]
    row["evidence_freshness"] = integrity["status"]
    repository.add(row)
    return deepcopy(row)


def add_shadow_observation(repository, key, observation, *, as_of):
    if not isinstance(observation, dict):
        raise ValueError("observation must be a mapping")
    _no_authority(observation)
    candidate = repository.get(key)
    require_operation(candidate.get("maturity_stage"), "shadow_observation")
    observed, now = _clock(observation.get("observed_at")), _clock(as_of)
    previous = repository.observations(key)
    baseline = _clock(previous[-1]["observed_at"] if previous else candidate["observed_at"])
    if observed <= baseline or observed > now:
        raise ValueError("observation must be later and not future")
    row = deepcopy(observation)
    row.update({"shadow_candidate_id": key, **SAFETY})
    integrity = evaluate_observation(candidate, row, as_of=as_of)
    row["freshness_status"] = integrity["status"]
    row["integrity_reasons"] = integrity["reasons"]
    repository.observe(key, row)
    return deepcopy(row)


def complete_shadow(repository, key, *, as_of):
    candidate = repository.get(key)
    require_operation(candidate.get("maturity_stage"), "shadow_outcome")
    now = _clock(as_of)
    rows = repository.observations(key)
    hold_days = (now - _clock(candidate["observed_at"])).total_seconds() / 86400
    if hold_days <= 0:
        raise ValueError("outcome must be later than acquisition observation")
    status, reasons, profit, refs = "insufficient_evidence", ["missing_observation"], None, []
    if rows:
        latest = rows[-1]
        if _clock(latest["observed_at"]) > now:
            raise ValueError("outcome precedes latest observation")
        if (not same_identity(candidate.get("product_identity"), latest.get("product_identity"))
                or latest.get("condition_changes") is True):
            status, reasons = "invalidated", ["observed_identity_or_condition_changed"]
        else:
            evaluation = observation_evaluation(candidate, latest)
            integrity = evaluate_observation(candidate, latest, as_of=as_of)
            reasons, refs = integrity["reasons"], integrity["evidence_refs"]
            if not reasons:
                profit = (evaluation["expected_sale_price"] - evaluation["expected_selling_fee"]
                          - evaluation["expected_outbound_shipping"] - candidate["total_acquisition_cost"])
                status = "success" if profit >= 0 else "loss"
            elif (latest.get("sellability_result") == "unsold" and number(candidate.get("max_hold_days"), minimum=1)
                  and hold_days >= candidate["max_hold_days"]
                  and reasons == ["insufficient_sold_evidence"]):
                status = "unsold"
    outcome = {"shadow_candidate_id": key, "outcome_at": now.isoformat(), "outcome_status": status,
               "hypothetical_profit": max(profit, 0) if profit is not None else None,
               "hypothetical_loss": max(-profit, 0) if profit is not None else None,
               "hypothetical_roi": profit / candidate["total_acquisition_cost"] if profit is not None else None,
               "estimated_hold_days": hold_days, "sellability_result": "supported" if profit is not None else status,
               "invalidation_reason": reasons[0] if status == "invalidated" else None,
               "reasons": reasons, "evidence_refs": refs, "hypothetical": True, **SAFETY}
    repository.finish(key, outcome)
    return deepcopy(outcome)
