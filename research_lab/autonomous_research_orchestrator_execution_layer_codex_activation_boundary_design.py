"""Design the inert activation boundary for a future Codex executor.

The boundary is intentionally non-executing. It translates a validated Codex
adapter snapshot into a local activation-review snapshot and preserves all
external execution permissions as disabled.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_codex_executor_adapter_validation import (
    validate_codex_executor_adapter_output,
)

CODEX_ACTIVATION_BOUNDARY_DESIGN_VERSION = "0.1"


def build_codex_activation_boundary_design(adapter):
    validation = validate_codex_executor_adapter_output(adapter)
    ready = (
        validation["valid"] is True
        and validation["ready_for_codex_activation_boundary"] is True
    )

    return {
        "version": CODEX_ACTIVATION_BOUNDARY_DESIGN_VERSION,
        "boundary_valid": validation["valid"] is True,
        "boundary_ready": ready,
        "provider": "codex",
        "branch": adapter.get("branch") if ready else None,
        "request_steps": adapter.get("request_steps", ()) if ready else (),
        "request_count": adapter.get("request_count", 0) if ready else 0,
        "human_gate_required_for_activation": ready,
        "activation_review_only": True,
        "codex_invocation_authorized": False,
        "codex_invoked": False,
        "network_access_authorized": False,
        "main_branch_authorized": False,
        "credentials_change_authorized": False,
        "production_change_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
        "external_action_performed": False,
    }


def validate_codex_activation_boundary_design():
    from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_handoff_boundary import (
        build_bounded_executor_handoff_boundary,
    )
    from research_lab.autonomous_research_orchestrator_execution_layer_codex_executor_adapter_design import (
        build_codex_executor_adapter_design,
    )

    adapter = build_codex_executor_adapter_design(
        build_bounded_executor_handoff_boundary(cycles_completed=9, repair_attempts=1)
    )
    boundary = build_codex_activation_boundary_design(adapter)

    assert boundary["boundary_valid"] is True
    assert boundary["boundary_ready"] is True
    assert boundary["provider"] == "codex"
    assert boundary["branch"] == "research-lab"
    assert boundary["request_count"] == 7
    assert boundary["human_gate_required_for_activation"] is True
    assert boundary["activation_review_only"] is True
    assert boundary["codex_invocation_authorized"] is False
    assert boundary["codex_invoked"] is False
    assert boundary["network_access_authorized"] is False
    assert boundary["external_action_authorized"] is False

    blocked_adapter = build_codex_executor_adapter_design(None)
    blocked = build_codex_activation_boundary_design(blocked_adapter)
    assert blocked["boundary_valid"] is True
    assert blocked["boundary_ready"] is False
    assert blocked["human_gate_required_for_activation"] is False
    assert blocked["request_steps"] == ()
    assert blocked["codex_invoked"] is False
    return True
