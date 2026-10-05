"""PG-037 stage contracts. Stage advancement never grants commerce authority."""
from research_lab.product_dd_input_gate import _utc_time

STAGES = (
    "research", "offline_validation", "shadow", "sandbox", "paper_commerce",
    "live_readiness", "human_gate", "limited_live", "burn_in", "controlled_automation",
)
EXTERNAL_OPERATIONS = (
    "real_purchase", "real_payment", "real_listing", "real_sale",
    "real_money_movement", "transfer", "refund",
)
_BASE = ("market_read", "evidence_save", "virtual_evaluation")
_EXTRA = {
    "offline_validation": ("offline_validation",),
    "shadow": ("shadow_candidate_save", "shadow_observation", "shadow_outcome"),
    "sandbox": ("sandbox_simulation",),
    "paper_commerce": ("paper_evaluation",),
    "live_readiness": ("readiness_evaluation",),
    "human_gate": ("human_review_preparation",),
}


def stage_contract(stage):
    if stage not in STAGES:
        raise ValueError("unknown maturity stage")
    index = STAGES.index(stage)
    allowed = _BASE + _EXTRA.get(stage, ())
    operations = set(_BASE + EXTERNAL_OPERATIONS)
    for extra in _EXTRA.values():
        operations.update(extra)
    return {
        "maturity_stage": stage, "stages": list(STAGES),
        "allowed": list(allowed), "forbidden": sorted(operations - set(allowed)),
        "next_stages": list(STAGES[index + 1:index + 2]),
        "human_gate_required": True, "external_execution_authorized": False,
        "purchase_authorized": False,
    }


def require_operation(stage, operation):
    if operation not in stage_contract(stage)["allowed"]:
        raise ValueError("operation forbidden by maturity contract")


def transition_stage(current, target, *, human_decision=None, readiness_audit=None, as_of=None):
    """Consume the existing human record; never synthesize or auto-pass it.

    The caller must obtain human_decision through the existing authenticated
    human workflow. This offline contract cannot authenticate a human itself.
    """
    if target not in stage_contract(current)["next_stages"]:
        raise ValueError("invalid stage transition")
    if current in ("human_gate", "limited_live", "burn_in"):
        from research_lab.human_go_no_go import build_human_go_no_go_decision
        decision = human_decision or {}
        audit = readiness_audit or {}
        now = _utc_time(as_of)
        if not isinstance(decision, dict) or not isinstance(audit, dict):
            raise ValueError("human decision and audit required")
        scope = decision.get("pilot_scope") or {}
        try:
            rebuilt = build_human_go_no_go_decision(
                audit, decision_key=decision.get("decision_key"), decision=decision.get("decision"),
                decided_at=decision.get("decided_at"), reviewer_id=decision.get("reviewer_id"),
                reason=decision.get("reason"), approved_budget_jpy=scope.get("approved_budget_jpy"),
                max_transactions=scope.get("max_transactions"),
                approved_providers=scope.get("approved_providers"), valid_until=decision.get("valid_until"),
            )
        except (ValueError, TypeError, AttributeError) as exc:
            raise ValueError("valid explicit human decision required") from exc
        if (decision != rebuilt or rebuilt["decision"] != "go" or not audit.get("audit_key")
                or now is None or not _utc_time(rebuilt["decided_at"]) <= now < _utc_time(rebuilt["valid_until"])):
            raise ValueError("human decision missing, mismatched, future or expired")
    return stage_contract(target)
