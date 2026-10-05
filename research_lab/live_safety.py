"""PG-047..050 fail-closed live-readiness, recovery, idempotency and burn-in."""
from statistics import mean

from research_lab.evidence_integrity import number

SAFETY = {
    "human_gate_required": True,
    "external_execution_authorized": False,
    "purchase_authorized": False,
}


def evaluate_live_readiness(
    *,
    integration,
    runtime,
    evidence,
    shadow_outcomes,
    promotion_pack,
    kill_switch_ready,
    max_loss_jpy,
):
    reasons = []
    if integration.get("integration_ready") is not True:
        reasons.append("integration_not_ready")
    if runtime.get("runtime_verified") is not True:
        reasons.append("runtime_not_verified")
    if evidence.get("passed") is not True:
        reasons.append("evidence_not_ready")
    if not isinstance(shadow_outcomes, list) or len(shadow_outcomes) < 3:
        reasons.append("insufficient_shadow_outcomes")
    elif any(row.get("status") != "success" for row in shadow_outcomes):
        reasons.append("shadow_outcome_failure")
    if promotion_pack.get("human_review_ready") is not True:
        reasons.append("promotion_pack_not_ready")
    if kill_switch_ready is not True:
        reasons.append("kill_switch_not_ready")
    if not number(max_loss_jpy) or max_loss_jpy <= 0:
        reasons.append("max_loss_not_defined")
    ready = not reasons
    return {
        "pg": "PG-047",
        "status": "live_readiness_ready" if ready else "live_readiness_blocked",
        "live_readiness_ready": ready,
        "reasons": reasons,
        "requires_explicit_human_go": True,
        **SAFETY,
    }


def recovery_decision(*, operation_class, failure_count, retryable, state_consistent):
    """PG-048. Reads may retry; commerce writes always fail closed."""
    if isinstance(failure_count, bool) or not isinstance(failure_count, int) or failure_count < 0:
        raise ValueError("invalid failure_count")
    if operation_class not in {"read", "research_write", "commerce_write"}:
        raise ValueError("unknown operation class")
    if operation_class == "read" and retryable is True and state_consistent is True and failure_count < 3:
        action = "retry_with_backoff"
    elif operation_class == "research_write" and retryable is True and state_consistent is True and failure_count < 2:
        action = "retry_once"
    else:
        action = "stop_and_escalate"
    return {
        "pg": "PG-048",
        "action": action,
        "fail_closed": action == "stop_and_escalate",
        **SAFETY,
    }


def evaluate_idempotency(*, operation_key, seen_operation_keys, payload_fingerprint):
    """PG-049 guard. A duplicate or ambiguous operation must not execute."""
    if not isinstance(operation_key, str) or not operation_key.strip():
        raise ValueError("operation_key required")
    if not isinstance(seen_operation_keys, dict):
        raise ValueError("seen_operation_keys mapping required")
    prior = seen_operation_keys.get(operation_key)
    duplicate = prior is not None
    same_payload = duplicate and prior == payload_fingerprint
    allowed_to_prepare = not duplicate
    return {
        "pg": "PG-049",
        "status": "new" if not duplicate else ("duplicate_same_payload" if same_payload else "duplicate_conflict"),
        "duplicate": duplicate,
        "payload_match": same_payload if duplicate else None,
        "prepare_only": allowed_to_prepare,
        "execute_authorized": False,
        **SAFETY,
    }


def evaluate_burn_in(
    outcomes,
    *,
    min_cases=5,
    min_success_rate=0.8,
    max_mean_abs_variance_jpy=250,
    max_loss_events=0,
):
    """PG-050 controlled burn-in evaluation from observed limited-live outcomes."""
    reasons = []
    if not isinstance(outcomes, list) or len(outcomes) < min_cases:
        reasons.append("insufficient_burn_in_cases")
    valid = [row for row in outcomes if isinstance(row, dict)]
    if len(valid) != len(outcomes):
        reasons.append("invalid_outcome_record")
    if valid:
        successes = [row for row in valid if row.get("status") == "success"]
        success_rate = len(successes) / len(valid)
        variances = [abs(row["forecast_variance"]) for row in valid if number(abs(row.get("forecast_variance", -1)))]
        loss_events = sum(1 for row in valid if number(row.get("realized_net_profit_jpy")) and row["realized_net_profit_jpy"] < 0)
        mean_abs_variance = mean(variances) if variances else None
    else:
        success_rate, loss_events, mean_abs_variance = 0.0, 0, None
    if success_rate < min_success_rate:
        reasons.append("burn_in_success_rate_low")
    if mean_abs_variance is None or mean_abs_variance > max_mean_abs_variance_jpy:
        reasons.append("burn_in_forecast_variance_high")
    if loss_events > max_loss_events:
        reasons.append("burn_in_loss_events_exceeded")
    passed = not reasons
    return {
        "pg": "PG-050",
        "status": "burn_in_passed" if passed else "burn_in_not_passed",
        "burn_in_passed": passed,
        "case_count": len(valid),
        "success_rate": success_rate,
        "mean_abs_forecast_variance_jpy": mean_abs_variance,
        "loss_events": loss_events,
        "reasons": reasons,
        "controlled_automation_ready": False,
        **SAFETY,
    }
