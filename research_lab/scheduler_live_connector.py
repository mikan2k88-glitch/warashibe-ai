"""Live scheduler connector contract for one hourly research slot.

This module reconciles the ChatGPT hourly supervisor schedule with the
research-lab CI state. It is deliberately decision-only: it does not trigger
GitHub, execute repairs, retry failures, or modify external systems.
"""

from datetime import datetime

_SCHEMA_VERSION = "1.0"
_ALLOWED_SOURCES = {"chatgpt_schedule", "github_actions_schedule"}
_ALLOWED_CI_STATES = {"not_started", "in_progress", "success", "failure"}


def _result(status, next_action, reason_code, slot=None, source=None):
    return {
        "scheduler_connector_schema_version": _SCHEMA_VERSION,
        "status": status,
        "next_action": next_action,
        "reason_code": reason_code,
        "slot": slot,
        "source": source,
        "read_only": True,
        "human_gate_required": False,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
    }


def _valid_hour_slot(slot):
    if not isinstance(slot, str):
        return False
    try:
        parsed = datetime.fromisoformat(slot.replace("Z", "+00:00"))
    except ValueError:
        return False
    return (
        parsed.tzinfo is not None
        and parsed.minute == 0
        and parsed.second == 0
        and parsed.microsecond == 0
    )


def decide_scheduler_live_connector(connector_input):
    """Return a bounded action for the current scheduler slot."""
    if not isinstance(connector_input, dict):
        return _result(
            "scheduler_connector_hold",
            "no_op",
            "invalid_connector_input",
        )

    slot = connector_input.get("slot")
    source = connector_input.get("source")
    ci_state = connector_input.get("ci_state", "not_started")
    current_head_sha = connector_input.get("current_head_sha")
    ci_head_sha = connector_input.get("ci_head_sha")

    if not _valid_hour_slot(slot):
        return _result(
            "scheduler_connector_hold",
            "no_op",
            "invalid_hourly_slot",
            slot=slot,
            source=source,
        )

    if source not in _ALLOWED_SOURCES:
        return _result(
            "scheduler_connector_hold",
            "no_op",
            "unknown_scheduler_source",
            slot=slot,
            source=source,
        )

    if ci_state not in _ALLOWED_CI_STATES:
        return _result(
            "scheduler_connector_hold",
            "no_op",
            "unknown_ci_state",
            slot=slot,
            source=source,
        )

    if connector_input.get("last_completed_slot") == slot:
        return _result(
            "scheduler_connector_skip",
            "no_op",
            "hourly_slot_already_completed",
            slot=slot,
            source=source,
        )

    if ci_state == "in_progress":
        return _result(
            "scheduler_connector_hold",
            "no_op",
            "ci_already_in_progress",
            slot=slot,
            source=source,
        )

    if ci_state == "failure":
        return _result(
            "scheduler_connector_hold",
            "no_op",
            "ci_failure_requires_research_review",
            slot=slot,
            source=source,
        )

    if ci_state == "success":
        if not current_head_sha or not ci_head_sha or current_head_sha != ci_head_sha:
            return _result(
                "scheduler_connector_hold",
                "no_op",
                "ci_sha_mismatch",
                slot=slot,
                source=source,
            )
        return _result(
            "scheduler_connector_skip",
            "no_op",
            "same_head_already_verified",
            slot=slot,
            source=source,
        )

    return _result(
        "scheduler_connector_ready",
        "run_research_cycle",
        "hourly_slot_due",
        slot=slot,
        source=source,
    )
