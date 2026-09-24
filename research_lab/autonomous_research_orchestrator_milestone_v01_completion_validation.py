"""Validate Autonomous Research Orchestrator v0.1 milestone completion records.

Pure validation only. Completion never authorizes external actions.
"""

from research_lab.autonomous_research_orchestrator_milestone_v01_completion import (
    ORCHESTRATOR_MILESTONE_V01_COMPLETION_VERSION,
)

ORCHESTRATOR_MILESTONE_V01_COMPLETION_VALIDATION_VERSION = "0.1"
VALID_STATUSES = ("quiet", "milestone_reached", "stopped", "blocked")


def validate_orchestrator_milestone_v01_completion_result(record):
    if not isinstance(record, dict):
        return {"valid": False, "reason": "orchestrator_v01_completion_not_mapping"}

    required = {
        "version", "record_valid", "orchestrator_v01_complete",
        "continue_autonomous_research", "human_gate_required", "status", "reason",
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
                    record["orchestrator_v01_complete"] is False
                    and record["continue_autonomous_research"] is True
                    and record["human_gate_required"] is False
                    and record["status"] == "quiet"
                    and record["reason"] == "autonomous_research_may_continue"
                )
                or (
                    record["orchestrator_v01_complete"] is True
                    and record["continue_autonomous_research"] is False
                    and record["human_gate_required"] is True
                    and record["status"] in ("milestone_reached", "stopped")
                    and record["reason"] == "orchestrator_v01_milestone_complete"
                )
            )
        )
        or (
            record["record_valid"] is False
            and record["orchestrator_v01_complete"] is False
            and record["continue_autonomous_research"] is False
            and record["human_gate_required"] is False
            and record["status"] == "blocked"
            and record["reason"] == "invalid_completion_summary"
        )
    )
    valid = (
        record["version"] == ORCHESTRATOR_MILESTONE_V01_COMPLETION_VERSION
        and all(isinstance(record[key], bool) for key in (
            "record_valid", "orchestrator_v01_complete",
            "continue_autonomous_research", "human_gate_required",
        ))
        and record["status"] in VALID_STATUSES
        and isinstance(record["reason"], str)
        and safe and state_consistent
    )
    return {
        "version": ORCHESTRATOR_MILESTONE_V01_COMPLETION_VALIDATION_VERSION,
        "valid": valid,
        "orchestrator_v01_complete": valid and record["orchestrator_v01_complete"],
        "may_continue_autonomous_research": valid and record["continue_autonomous_research"],
        "human_gate_required": valid and record["human_gate_required"],
        "reason": "orchestrator_v01_completion_validated" if valid else "invalid_orchestrator_v01_completion",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }


def validate_orchestrator_milestone_v01_completion_validation():
    from research_lab.autonomous_research_orchestrator_milestone_v01_completion import orchestrator_milestone_v01_completion

    blocked = orchestrator_milestone_v01_completion(None)
    result = validate_orchestrator_milestone_v01_completion_result(blocked)
    assert result["valid"] is True
    assert result["orchestrator_v01_complete"] is False
    assert result["may_continue_autonomous_research"] is False

    tampered = dict(blocked)
    tampered["production_changed"] = True
    assert validate_orchestrator_milestone_v01_completion_result(tampered)["valid"] is False
    return True
