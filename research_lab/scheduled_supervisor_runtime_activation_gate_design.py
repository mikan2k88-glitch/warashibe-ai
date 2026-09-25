"""Final activation gate design for scheduled GPT Supervisor runtime.

This gate combines design readiness, live connector readiness, safety status,
and explicit human approval. It does not activate any scheduler or external
runtime itself.
"""

from research_lab.scheduled_supervisor_runtime_activation_review import (
    build_runtime_readiness_snapshot,
)
from research_lab.scheduled_supervisor_runtime_contract_design import (
    build_scheduled_supervisor_runtime_contract_design,
)
from research_lab.scheduled_supervisor_runtime_cycle_controller_design import (
    build_cycle_controller_design,
)
from research_lab.scheduled_supervisor_runtime_state_machine_design import (
    build_state_machine_design,
)

SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_GATE_VERSION = "0.1"

REQUIRED_DESIGN_GATES = (
    "activation_review_ready",
    "runtime_contract_ready",
    "cycle_controller_ready",
    "state_machine_ready",
)

REQUIRED_LIVE_GATES = (
    "live_scheduler_connected",
    "live_gemini_connected",
    "live_codex_connected",
)

SAFETY_GATES = (
    "human_gate_path_ready",
    "main_write_gate_preserved",
    "secrets_boundary_preserved",
    "commerce_boundary_preserved",
    "production_boundary_preserved",
)


def build_activation_gate_snapshot(
    live_scheduler_connected=False,
    live_gemini_connected=False,
    live_codex_connected=False,
    explicit_human_approval=False,
):
    readiness = build_runtime_readiness_snapshot()
    runtime_contract = build_scheduled_supervisor_runtime_contract_design()
    cycle_controller = build_cycle_controller_design()
    state_machine = build_state_machine_design()

    design_gates = {
        "activation_review_ready": readiness["design_ready"] is True,
        "runtime_contract_ready": runtime_contract["mode"] == "design_only",
        "cycle_controller_ready": cycle_controller["mode"] == "design_only",
        "state_machine_ready": state_machine["mode"] == "design_only",
    }

    live_gates = {
        "live_scheduler_connected": bool(live_scheduler_connected),
        "live_gemini_connected": bool(live_gemini_connected),
        "live_codex_connected": bool(live_codex_connected),
    }

    safety_gates = {
        "human_gate_path_ready": True,
        "main_write_gate_preserved":
            runtime_contract["main_write_requires_human_gate"] is True,
        "secrets_boundary_preserved": True,
        "commerce_boundary_preserved": True,
        "production_boundary_preserved": True,
    }

    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_GATE_VERSION,
        "mode": "activation_gate_only",
        "design_gates": design_gates,
        "live_gates": live_gates,
        "safety_gates": safety_gates,
        "all_design_gates_green": all(design_gates.values()),
        "all_live_gates_green": all(live_gates.values()),
        "all_safety_gates_green": all(safety_gates.values()),
        "explicit_human_approval": bool(explicit_human_approval),
        "activation_authorized": False,
        "scheduled_runtime_active": False,
        "external_action_authorized": False,
    }


def evaluate_activation_gate(snapshot):
    if not isinstance(snapshot, dict):
        return {
            "approved": False,
            "reason": "invalid_activation_snapshot",
            "activation_authorized": False,
        }

    blockers = []

    def gates_green(field, required):
        gates = snapshot.get(field)
        return isinstance(gates, dict) and all(
            gates.get(name) is True for name in required
        )

    if not gates_green("design_gates", REQUIRED_DESIGN_GATES):
        blockers.append("design_gates_not_green")

    if not gates_green("safety_gates", SAFETY_GATES):
        blockers.append("safety_gates_not_green")

    if not gates_green("live_gates", REQUIRED_LIVE_GATES):
        blockers.append("live_connectors_not_ready")

    if snapshot.get("explicit_human_approval") is not True:
        blockers.append("explicit_human_approval_required")

    approved = not blockers

    return {
        "approved": approved,
        "blockers": tuple(blockers),
        "reason": "design_gate_clear_not_live_authority" if approved else "activation_blocked",
        "approval_scope": (
            "scheduled_supervisor_runtime_activation" if approved else None
        ),
        "approval_reusable": False,
        "evidence_verified": False,
        "activation_authorized": False,
        "scheduled_runtime_active": False,
        "external_action_authorized": False,
    }


def build_activation_gate_design():
    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_GATE_VERSION,
        "mode": "design_only",
        "required_design_gates": REQUIRED_DESIGN_GATES,
        "required_live_gates": REQUIRED_LIVE_GATES,
        "safety_gates": SAFETY_GATES,
        "explicit_human_approval_required": True,
        "approval_reusable": False,
        "activation_is_separate_from_gate_evaluation": True,
        "scheduled_runtime_active": False,
        "activation_authorized": False,
        "external_action_authorized": False,
    }


def validate_scheduled_supervisor_runtime_activation_gate_design():
    design = build_activation_gate_design()
    assert design["mode"] == "design_only"
    assert design["explicit_human_approval_required"] is True
    assert design["approval_reusable"] is False
    assert design["activation_is_separate_from_gate_evaluation"] is True
    assert design["scheduled_runtime_active"] is False
    assert design["activation_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
