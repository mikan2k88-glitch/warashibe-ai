"""Completion review for the real-world core milestone."""

from research_lab.warashibe_core_milestone_validation import (
    validate_real_world_core_milestone,
)

MILESTONE_COMPLETION_REVIEW_VERSION = "0.1"


def review_milestone_completion():
    validation = validate_real_world_core_milestone()

    blockers = []
    if not validation.get("passed"):
        blockers.append("milestone_validation_failed")
    if validation.get("terminal_status") != "ready_for_human_gate":
        blockers.append("unexpected_terminal_status")
    if validation.get("execution_authorized") is not False:
        blockers.append("execution_boundary_open")
    if validation.get("commerce_authorized") is not False:
        blockers.append("commerce_boundary_open")
    if validation.get("main_branch_change_authorized") is not False:
        blockers.append("main_branch_boundary_open")
    if validation.get("production_change_authorized") is not False:
        blockers.append("production_boundary_open")

    completed = not blockers

    return {
        "version": MILESTONE_COMPLETION_REVIEW_VERSION,
        "milestone": "real_world_core_to_human_gate",
        "completed": completed,
        "blockers": tuple(blockers),
        "validation": validation,
        "completion_state": (
            "milestone_complete"
            if completed
            else "milestone_incomplete"
        ),
        "next_milestone": (
            "sandbox_external_integration"
            if completed
            else "repair_current_milestone"
        ),
        "main_merge_authorized": False,
        "production_rollout_authorized": False,
        "external_execution_authorized": False,
        "commerce_authorized": False,
    }
