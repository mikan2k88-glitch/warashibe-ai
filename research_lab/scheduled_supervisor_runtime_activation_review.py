"""Review readiness for scheduled GPT Supervisor runtime activation.

This module checks whether the supervisory closed-loop design is mature enough
to move from design-only operation toward a scheduled runtime. It does not
create a scheduler, call Gemini, invoke Codex, commit code, or perform commerce.
"""

from research_lab.closed_loop_milestone_validation import (
    validate_closed_loop_milestone,
)

SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_REVIEW_VERSION = "0.1"

RUNTIME_COMPONENTS = (
    "scheduler_trigger",
    "gpt_supervisor",
    "gemini_orchestrator",
    "codex_worker",
    "safety_kernel_ci",
)

ACTIVATION_GATES = (
    "closed_loop_milestone_green",
    "scheduler_contract_defined",
    "gemini_runtime_boundary_defined",
    "codex_runtime_boundary_defined",
    "human_gate_path_defined",
    "failure_stop_policy_defined",
)


def build_runtime_readiness_snapshot():
    milestone = validate_closed_loop_milestone()

    gates = {
        "closed_loop_milestone_green": milestone["passed"] is True,
        "scheduler_contract_defined": True,
        "gemini_runtime_boundary_defined": True,
        "codex_runtime_boundary_defined": True,
        "human_gate_path_defined": True,
        "failure_stop_policy_defined": True,
    }

    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_REVIEW_VERSION,
        "mode": "activation_review_only",
        "runtime_components": RUNTIME_COMPONENTS,
        "activation_gates": gates,
        "design_ready": all(gates.values()),
        "live_scheduler_connected": False,
        "live_gemini_connected": False,
        "live_codex_connected": False,
        "scheduled_runtime_active": False,
        "runtime_activation_authorized": False,
        "external_action_authorized": False,
    }


def review_runtime_activation():
    snapshot = build_runtime_readiness_snapshot()
    blockers = []

    if not snapshot["design_ready"]:
        blockers.append("design_gate_not_ready")

    if not snapshot["live_scheduler_connected"]:
        blockers.append("live_scheduler_not_connected")

    if not snapshot["live_gemini_connected"]:
        blockers.append("live_gemini_not_connected")

    if not snapshot["live_codex_connected"]:
        blockers.append("live_codex_not_connected")

    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_REVIEW_VERSION,
        "design_ready": snapshot["design_ready"],
        "runtime_ready": not blockers,
        "blockers": tuple(blockers),
        "recommended_next_step": (
            "scheduled_supervisor_runtime_contract_design"
            if snapshot["design_ready"]
            else "repair_closed_loop_design"
        ),
        "runtime_activation_authorized": False,
        "scheduled_runtime_active": False,
        "external_action_authorized": False,
    }


def validate_scheduled_supervisor_runtime_activation_review():
    snapshot = build_runtime_readiness_snapshot()
    review = review_runtime_activation()

    assert snapshot["mode"] == "activation_review_only"
    assert snapshot["design_ready"] is True
    assert snapshot["live_scheduler_connected"] is False
    assert snapshot["live_gemini_connected"] is False
    assert snapshot["live_codex_connected"] is False
    assert snapshot["runtime_activation_authorized"] is False

    assert review["design_ready"] is True
    assert review["runtime_ready"] is False
    assert "live_scheduler_not_connected" in review["blockers"]
    assert "live_gemini_not_connected" in review["blockers"]
    assert "live_codex_not_connected" in review["blockers"]
    assert (
        review["recommended_next_step"]
        == "scheduled_supervisor_runtime_contract_design"
    )
    assert review["runtime_activation_authorized"] is False
    assert review["scheduled_runtime_active"] is False
    assert review["external_action_authorized"] is False
    return True
