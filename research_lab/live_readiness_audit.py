"""PG-024 Live-readiness Audit.

This audit aggregates evidence from PG-011..PG-023 and determines only whether
a human go/no-go review may be performed. It never enables live commerce.
"""

from datetime import datetime, timezone

AUDIT_VERSION = "0.1"

_REQUIRED_TRUE = (
    "identity_match_verified",
    "physical_policy_passed",
    "freshness_passed",
    "human_review_approved",
    "economics_viable",
    "preflight_ready",
    "pilot_session_ready",
    "purchase_intent_valid",
    "sandbox_adapter_verified",
    "duplicate_transaction_guard",
    "single_item_guard",
    "parallel_positions_disabled",
    "rls_enabled",
    "public_anon_write_policy_absent",
    "audit_cleanup_verified",
    "live_commerce_block_enabled",
    "rollback_plan_documented",
    "refund_cancel_path_documented",
    "marketplace_terms_review_required",
    "secrets_server_side_only",
)

_REQUIRED_FALSE = (
    "sandbox_network_call_attempted",
    "sandbox_external_write_attempted",
)


def _require_text(value, name, *, max_length=300):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")
    value=value.strip()
    if len(value)>max_length:
        raise ValueError(f"{name} is too long")
    return value


def _parse_utc(value, name):
    value=_require_text(value,name,max_length=80)
    text=value[:-1]+"+00:00" if value.endswith("Z") else value
    dt=datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"{name} must include timezone")
    return dt.astimezone(timezone.utc)


def evaluate_live_readiness(evidence, *, audit_key, audited_at, auditor_id):
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be a dictionary")

    checks={}
    failed=[]

    for key in _REQUIRED_TRUE:
        passed=evidence.get(key) is True
        checks[key]={"expected":True,"actual":evidence.get(key),"passed":passed}
        if not passed:
            failed.append(key)

    for key in _REQUIRED_FALSE:
        passed=evidence.get(key) is False
        checks[key]={"expected":False,"actual":evidence.get(key),"passed":passed}
        if not passed:
            failed.append(key)

    all_passed=not failed

    return {
        "version":AUDIT_VERSION,
        "status":"live_readiness_audit_complete",
        "audit_key":_require_text(audit_key,"audit_key",max_length=200),
        "audited_at":_parse_utc(audited_at,"audited_at").isoformat(),
        "auditor_id":_require_text(auditor_id,"auditor_id",max_length=100),
        "checks":checks,
        "failed_checks":failed,
        "required_check_count":len(checks),
        "passed_check_count":sum(1 for item in checks.values() if item["passed"]),
        "all_required_checks_passed":all_passed,
        "ready_for_human_go_no_go":all_passed,
        "human_go_no_go_required":True,
        "recommended_next_stage":"human_live_pilot_decision" if all_passed else "repair_readiness_gaps",
        "live_commerce_authorized":False,
        "execution_mode":"audit_only",
        "execution_triggered":False,
        "commerce_authorized":False,
        "external_action_authorized":False,
        "purchase_authorized":False,
        "payment_authorized":False,
        "sale_authorized":False,
    }
