"""Validate the local Autonomous Research Orchestrator v0.1 milestone record.

Validation is fail-closed and grants no external-action permission.
"""

from research_lab.autonomous_research_orchestrator_v01_milestone_record import (
    ORCHESTRATOR_V01_MILESTONE_RECORD_VERSION,
)

ORCHESTRATOR_V01_MILESTONE_RECORD_VALIDATION_VERSION = "0.1"
VALID_STATUSES = ("quiet", "milestone_reached", "stopped", "blocked")


def validate_orchestrator_v01_milestone_record_result(record):
    if not isinstance(record, dict):
        return {"valid": False, "reason": "orchestrator_v01_milestone_record_not_mapping"}

    required = {
        "version", "record_valid", "milestone", "milestone_complete",
        "human_gate_required", "continue_autonomous_research", "status", "reason",
        "external_action_authorized", "external_action_performed",
        "notification_sent", "credentials_included", "production_changed",
        "commerce_executed",
    }
    missing = tuple(sorted(required - set(record)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = all(record[key] is False for key in (
        "external_action_authorized", "external_action_performed",
        "notification_sent", "credentials_included", "production_changed",
        "commerce_executed",
    ))
    state_consistent = (
        (
            record["record_valid"] is True
            and (
                (
                    record["milestone_complete"] is True
                    and record["human_gate_required"] is True
                    and record["continue_autonomous_research"] is False
                    and record["status"] in ("milestone_reached", "stopped")
                    and record["reason"] == "v01_milestone_recorded"
                )
                or (
                    record["milestone_complete"] is False
                    and record["human_gate_required"] is False
                    and record["continue_autonomous_research"] is True
                    and record["status"] == "quiet"
                    and record["reason"] == "v01_milestone_in_progress"
                )
            )
        )
        or (
            record["record_valid"] is False
            and record["milestone_complete"] is False
            and record["human_gate_required"] is False
            and record["continue_autonomous_research"] is False
            and record["status"] == "blocked"
            and record["reason"] == "invalid_v01_completion"
        )
    )
    valid = (
        record["version"] == ORCHESTRATOR_V01_MILESTONE_RECORD_VERSION
        and record["milestone"] == "autonomous_research_orchestrator_v0.1"
        and all(isinstance(record[key], bool) for key in (
            "record_valid", "milestone_complete", "human_gate_required",
            "continue_autonomous_research",
        ))
        and record["status"] in VALID_STATUSES
        and isinstance(record["reason"], str)
        and safe and state_consistent
    )
    return {
        "version": ORCHESTRATOR_V01_MILESTONE_RECORD_VALIDATION_VERSION,
        "valid": valid,
        "milestone_complete": valid and record["milestone_complete"],
        "may_continue_autonomous_research": valid and record["continue_autonomous_research"],
        "human_gate_required": valid and record["human_gate_required"],
        "reason": "orchestrator_v01_milestone_record_validated" if valid else "invalid_orchestrator_v01_milestone_record",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }


def validate_orchestrator_v01_milestone_record_validation():
    from research_lab.autonomous_research_orchestrator_v01_milestone_record import orchestrator_v01_milestone_record

    blocked = orchestrator_v01_milestone_record(None)
    result = validate_orchestrator_v01_milestone_record_result(blocked)
    assert result["valid"] is True
    assert result["milestone_complete"] is False
    assert result["may_continue_autonomous_research"] is False

    tampered = dict(blocked)
    tampered["notification_sent"] = True
    assert validate_orchestrator_v01_milestone_record_result(tampered)["valid"] is False
    return True
