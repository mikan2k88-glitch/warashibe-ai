"""Strategy Learning Loop for Warashibe AI.

Turns web/research findings into bounded strategy-update proposals, validates
them against evidence requirements, and returns an adopt/reject decision.
This module never executes commerce or changes production policy by itself.
"""

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
):
    if not isinstance(proposal, dict):
        raise ValueError("proposal must be a mapping")
    if proposal.get("status") != "strategy_learning_proposal_ready":
        raise ValueError("strategy_learning_proposal_ready required")

    findings = _as_findings(proposal.get("findings") or [])
    sources = {row["source_url"] for row in findings}
    issues = []
    if len(findings) < minimum_findings:
        issues.append("insufficient_findings")
    if len(sources) < minimum_distinct_sources:
        issues.append("insufficient_distinct_sources")

    updates = proposal.get("proposed_rule_updates") or {}
    for key, value in updates.items():
        if key.endswith("_jpy_max") or key.endswith("_jpy_min") or key.endswith("_days"):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
                issues.append(f"invalid_{key}")
        if key.endswith("_score"):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
                issues.append(f"invalid_{key}")

    return {
        "status": "strategy_learning_validation_complete",
        "valid": not issues,
        "issues": issues,
        "finding_count": len(findings),
        "distinct_source_count": len(sources),
        "proposed_rule_updates": dict(updates),
        "external_execution_authorized": False,
    }


def decide_strategy_learning_update(proposal, validation):
    if not isinstance(validation, dict):
        raise ValueError("validation must be a mapping")
    if validation.get("status") != "strategy_learning_validation_complete":
        raise ValueError("strategy_learning_validation_complete required")

    adopted = validation.get("valid") is True
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


def run_strategy_learning_loop(*, findings, proposed_rule_updates, rationale):
    proposal = build_strategy_learning_proposal(
        findings=findings,
        proposed_rule_updates=proposed_rule_updates,
        rationale=rationale,
    )
    validation = validate_strategy_learning_proposal(proposal)
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
