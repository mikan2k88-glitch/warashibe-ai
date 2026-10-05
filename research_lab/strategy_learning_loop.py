"""Strategy Learning Loop for Warashibe AI.

Turns web/research findings into bounded strategy-update proposals, validates
them against evidence requirements, and returns an adopt/reject decision.
This module never executes commerce or changes production policy by itself.
"""

from datetime import datetime, timedelta, timezone
from copy import deepcopy
from research_lab.evidence_integrity import canonical_source, number
from research_lab.product_dd_input_gate import _utc_time

LEARNING_TOPICS = (
    "market_price_spread",
    "selling_fee",
    "shipping_cost",
    "liquidity",
    "seasonality",
    "failure_pattern",
)

ALLOWED_RULE_KEYS = {
    "target_total_acquisition_cost_jpy_max",
    "target_net_profit_jpy_min",
    "target_max_hold_days",
    "target_min_liquidity_score",
}


def _as_findings(findings):
    if not isinstance(findings, list):
        raise ValueError("findings must be a list")
    clean = []
    for row in findings:
        if not isinstance(row, dict):
            raise ValueError("each finding must be a mapping")
        topic = str(row.get("topic") or "")
        if topic not in LEARNING_TOPICS:
            raise ValueError("unsupported learning topic")
        source_url = str(row.get("source_url") or "")
        observed_at = str(row.get("observed_at") or "")
        evidence = row.get("evidence")
        if not source_url.startswith(("https://", "http://")):
            raise ValueError("source_url required")
        if not observed_at:
            raise ValueError("observed_at required")
        if evidence in (None, "", [], {}):
            raise ValueError("evidence required")
        clean.append(dict(row))
    return clean


def build_strategy_learning_proposal(*, findings, proposed_rule_updates, rationale):
    findings = _as_findings(findings)
    if not isinstance(proposed_rule_updates, dict) or not proposed_rule_updates:
        raise ValueError("proposed_rule_updates must be a non-empty mapping")
    unknown = set(proposed_rule_updates) - ALLOWED_RULE_KEYS
    if unknown:
        raise ValueError(f"unsupported strategy rule keys: {sorted(unknown)}")
    if not str(rationale or "").strip():
        raise ValueError("rationale required")

    return {
        "status": "strategy_learning_proposal_ready",
        "finding_count": len(findings),
        "topics": sorted({row["topic"] for row in findings}),
        "findings": findings,
        "proposed_rule_updates": dict(proposed_rule_updates),
        "rationale": str(rationale).strip(),
        "production_rule_changed": False,
        "external_execution_authorized": False,
    }


def validate_strategy_learning_proposal(
    proposal,
    *,
    minimum_findings=2,
    minimum_distinct_sources=2,
    as_of=None,
    max_age_days=7,
):
    if not isinstance(proposal, dict):
        raise ValueError("proposal must be a mapping")
    if proposal.get("status") != "strategy_learning_proposal_ready":
        raise ValueError("strategy_learning_proposal_ready required")

    findings = _as_findings(proposal.get("findings") or [])
    sources = {canonical_source(row["source_url"]) for row in findings}
    sources.discard(None)
    issues = []
    clock = as_of or datetime.now(timezone.utc).isoformat()
    now = _utc_time(clock)
    if (now is None or not number(max_age_days, minimum=0.000001) or max_age_days > 36500
            or any(isinstance(x, bool) or not isinstance(x, int) or x < 1
                   for x in (minimum_findings, minimum_distinct_sources))):
        raise ValueError("valid evidence clock and thresholds required")
    for row in findings:
        timestamp = row["observed_at"]
        # Legacy day-only findings explicitly mean UTC midnight.
        if isinstance(timestamp, str) and len(timestamp) == 10:
            timestamp += "T00:00:00+00:00"
        at = _utc_time(timestamp)
        if at is None or at > now or now - at > timedelta(days=max_age_days):
            issues.append("stale_future_or_invalid_finding_time")
        if canonical_source(row["source_url"]) is None:
            issues.append("invalid_finding_source")
    if len(findings) < minimum_findings:
        issues.append("insufficient_findings")
    if len(sources) < minimum_distinct_sources:
        issues.append("insufficient_distinct_sources")

    updates = proposal.get("proposed_rule_updates") or {}
    if not isinstance(updates, dict) or not updates or set(updates) - ALLOWED_RULE_KEYS:
        raise ValueError("non-empty allowed rule updates required")
    for key, value in updates.items():
        if key.endswith("_jpy_max") or key.endswith("_jpy_min") or key.endswith("_days"):
            if not number(value, minimum=0.000001):
                issues.append(f"invalid_{key}")
        if key.endswith("_score"):
            if not number(value) or value > 1:
                issues.append(f"invalid_{key}")

    return {
        "status": "strategy_learning_validation_complete",
        "valid": not issues,
        "issues": list(dict.fromkeys(issues)),
        "finding_count": len(findings),
        "distinct_source_count": len(sources),
        "proposed_rule_updates": dict(updates),
        "external_execution_authorized": False,
        "evaluated_at": clock,
        "minimum_findings": minimum_findings,
        "minimum_distinct_sources": minimum_distinct_sources,
        "max_age_days": max_age_days,
        "validated_proposal": deepcopy(proposal),
    }


def decide_strategy_learning_update(proposal, validation):
    if not isinstance(validation, dict):
        raise ValueError("validation must be a mapping")
    if validation.get("status") != "strategy_learning_validation_complete":
        raise ValueError("strategy_learning_validation_complete required")

    fresh = validate_strategy_learning_proposal(
        proposal, as_of=validation.get("evaluated_at"),
        minimum_findings=validation.get("minimum_findings", 2),
        minimum_distinct_sources=validation.get("minimum_distinct_sources", 2),
        max_age_days=validation.get("max_age_days", 7))
    adopted = (validation.get("valid") is True and fresh["valid"]
               and validation.get("validated_proposal") == proposal
               and validation.get("proposed_rule_updates") == proposal.get("proposed_rule_updates"))
    return {
        "status": "strategy_learning_decision_ready",
        "decision": "adopt_for_p2_evaluation" if adopted else "reject",
        "reason": "evidence_gate_passed" if adopted else "evidence_gate_failed",
        "rule_updates": dict(proposal.get("proposed_rule_updates") or {}) if adopted else {},
        "requires_shadow_validation": adopted,
        "production_rule_changed": False,
        "human_gate_preserved": True,
        "external_execution_authorized": False,
    }


def run_strategy_learning_loop(*, findings, proposed_rule_updates, rationale, as_of=None):
    proposal = build_strategy_learning_proposal(
        findings=findings,
        proposed_rule_updates=proposed_rule_updates,
        rationale=rationale,
    )
    validation = validate_strategy_learning_proposal(proposal, as_of=as_of)
    decision = decide_strategy_learning_update(proposal, validation)
    return {
        "status": "strategy_learning_loop_complete",
        "proposal": proposal,
        "validation": validation,
        "decision": decision,
        "next_action": (
            "shadow_validate_rule_updates"
            if decision["decision"] == "adopt_for_p2_evaluation"
            else "collect_more_evidence"
        ),
        "production_rule_changed": False,
        "external_execution_authorized": False,
    }


__all__ = [
    "LEARNING_TOPICS",
    "ALLOWED_RULE_KEYS",
    "build_strategy_learning_proposal",
    "validate_strategy_learning_proposal",
    "decide_strategy_learning_update",
    "run_strategy_learning_loop",
]
