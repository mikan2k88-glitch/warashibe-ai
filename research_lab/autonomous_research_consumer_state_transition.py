"""AI-side state transition after consumer audit verification.

This module converts the consumer-facing audit decision into a bounded research
state. It does not execute repairs, retries, external actions, or rollbacks.
The AI is allowed to choose the next research state without a human gate;
execution remains separately bounded by the research-lab policy and CI gates.
"""

_SCHEMA_VERSION = "1.0"


def _result(next_state, action, reason_code, *, status="consumer_state_transition_ready"):
    return {
        "state_transition_schema_version": _SCHEMA_VERSION,
        "status": status,
        "next_state": next_state,
        "action": action,
        "reason_code": reason_code,
        "read_only": True,
        "human_gate_required": False,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
    }


def decide_consumer_state_transition(consumer_result):
    """Map a consumer verification result to the next bounded research state."""
    if not isinstance(consumer_result, dict):
        return _result(
            "await_more_evidence",
            "schedule_recheck",
            "invalid_consumer_result",
            status="consumer_state_transition_hold",
        )

    decision = consumer_result.get("decision")
    integrity_verified = consumer_result.get("integrity_verified") is True

    if decision == "accept":
        if not integrity_verified:
            return _result(
                "await_more_evidence",
                "schedule_recheck",
                "accept_without_integrity",
                status="consumer_state_transition_hold",
            )
        return _result(
            "advance_to_next_theme",
            "continue_research",
            "audit_bundle_verified",
        )

    if decision == "reject":
        return _result(
            "repair_current_audit",
            "prepare_repair_candidate",
            "audit_bundle_rejected",
        )

    if decision == "hold":
        return _result(
            "await_more_evidence",
            "schedule_recheck",
            "audit_bundle_on_hold",
        )

    return _result(
        "await_more_evidence",
        "schedule_recheck",
        "unknown_consumer_decision",
        status="consumer_state_transition_hold",
    )
