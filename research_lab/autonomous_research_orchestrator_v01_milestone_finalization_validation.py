"""Validate Autonomous Research Orchestrator v0.1 milestone finalization.

Pure validation only. A finalized milestone remains stopped at the human gate.
"""

from research_lab.autonomous_research_orchestrator_v01_milestone_finalization import (
    ORCHESTRATOR_V01_MILESTONE_FINALIZATION_VERSION,
)

ORCHESTRATOR_V01_MILESTONE_FINALIZATION_VALIDATION_VERSION = "0.1"
VALID_STATUSES = ("quiet", "milestone_reached", "stopped", "blocked")


def validate_orchestrator_v01_milestone_finalization_result(finalization):
    if not isinstance(finalization, dict):
        return {"valid": False, "reason": "orchestrator_v01_finalization_not_mapping"}

    required = {
        "version", "finalization_valid", "orchestrator_v01_finalized",
        "continue_autonomous_research", "human_gate_required", "status", "reason",
        "external_action_authorized", "external_action_performed",
        "notification_sent", "credentials_included", "production_changed",
        "commerce_executed",
    }
    missing = tuple(sorted(required - set(finalization)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = all(finalization[key] is False for key in (
        "external_action_authorized", "external_action_performed",
        "notification_sent", "credentials_included", "production_changed",
        "commerce_executed",
    ))
    state_consistent = (
        (
            finalization["finalization_valid"] is True
            and (
                (
                    finalization["orchestrator_v01_finalized"] is True
                    and finalization["continue_autonomous_research"] is False
                    and finalization["human_gate_required"] is True
                    and finalization["status"] in ("milestone_reached", "stopped")
                    and finalization["reason"] == "orchestrator_v01_finalized"
                )
                or (
                    finalization["orchestrator_v01_finalized"] is False
                    and finalization["continue_autonomous_research"] is True
                    and finalization["human_gate_required"] is False
                    and finalization["status"] == "quiet"
                    and finalization["reason"] == "orchestrator_v01_not_complete"
                )
            )
        )
        or (
            finalization["finalization_valid"] is False
            and finalization["orchestrator_v01_finalized"] is False
            and finalization["continue_autonomous_research"] is False
            and finalization["human_gate_required"] is False
            and finalization["status"] == "blocked"
            and finalization["reason"] == "invalid_v01_milestone_record"
        )
    )
    valid = (
        finalization["version"] == ORCHESTRATOR_V01_MILESTONE_FINALIZATION_VERSION
        and all(isinstance(finalization[key], bool) for key in (
            "finalization_valid", "orchestrator_v01_finalized",
            "continue_autonomous_research", "human_gate_required",
        ))
        and finalization["status"] in VALID_STATUSES
        and isinstance(finalization["reason"], str)
        and safe and state_consistent
    )
    return {
        "version": ORCHESTRATOR_V01_MILESTONE_FINALIZATION_VALIDATION_VERSION,
        "valid": valid,
        "orchestrator_v01_finalized": valid and finalization["orchestrator_v01_finalized"],
        "may_continue_autonomous_research": valid and finalization["continue_autonomous_research"],
        "human_gate_required": valid and finalization["human_gate_required"],
        "reason": "orchestrator_v01_finalization_validated" if valid else "invalid_orchestrator_v01_finalization",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }


def validate_orchestrator_v01_milestone_finalization_validation():
    from research_lab.autonomous_research_orchestrator_v01_milestone_finalization import orchestrator_v01_milestone_finalization

    blocked = orchestrator_v01_milestone_finalization(None)
    result = validate_orchestrator_v01_milestone_finalization_result(blocked)
    assert result["valid"] is True
    assert result["orchestrator_v01_finalized"] is False
    assert result["may_continue_autonomous_research"] is False

    tampered = dict(blocked)
    tampered["external_action_authorized"] = True
    assert validate_orchestrator_v01_milestone_finalization_result(tampered)["valid"] is False
    return True
