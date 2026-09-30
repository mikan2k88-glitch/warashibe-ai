"""Bounded hourly scheduler contract for autonomous research cycles.

The scheduler translates the AI consumer state into a single hourly action.
It does not perform repairs, retries, rollbacks, external actions, or commits.
The human gate remains disabled for the research-lab decision path.
"""

from datetime import datetime

_SCHEMA_VERSION = "1.0"


def _result(status, next_action, reason_code, slot=None):
    return {
        "hourly_schedule_schema_version": _SCHEMA_VERSION,
        "status": status,
        "next_action": next_action,
        "reason_code": reason_code,
        "slot": slot,
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


def decide_hourly_research_schedule(schedule_input):
    """Choose the next bounded hourly research action from AI state."""
    if not isinstance(schedule_input, dict):
        return _result(
            "hourly_schedule_hold",
            "schedule_recheck",
            "invalid_schedule_input",
        )

    slot = schedule_input.get("slot")
    if not _valid_hour_slot(slot):
        return _result(
            "hourly_schedule_hold",
            "schedule_recheck",
            "invalid_hourly_slot",
            slot=slot,
        )

    if schedule_input.get("last_completed_slot") == slot:
        return _result(
            "hourly_schedule_skip",
            "no_op",
            "hourly_slot_already_completed",
            slot=slot,
        )

    decision = schedule_input.get("decision")
    if decision == "advance_to_next_theme":
        return _result(
            "hourly_schedule_ready",
            "run_research_cycle",
            "hourly_slot_due",
            slot=slot,
        )

    if decision == "repair_current_audit":
        return _result(
            "hourly_schedule_ready",
            "prepare_repair_candidate",
            "repair_state_due",
            slot=slot,
        )

    if decision == "hold":
        return _result(
            "hourly_schedule_hold",
            "schedule_recheck",
            "consumer_state_hold",
            slot=slot,
        )

    return _result(
        "hourly_schedule_hold",
        "schedule_recheck",
        "unknown_consumer_state",
        slot=slot,
    )
