"""Design a fail-closed adapter contract for a future Codex executor.

This module is deliberately inert. It converts a validated bounded-executor
handoff into a local adapter design snapshot only; it never invokes Codex,
opens a network connection, changes credentials, or performs repository work.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_handoff_boundary_validation import (
    validate_bounded_executor_handoff_boundary_output,
)

CODEX_EXECUTOR_ADAPTER_DESIGN_VERSION = "0.1"


def build_codex_executor_adapter_design(handoff):
    validation = validate_bounded_executor_handoff_boundary_output(handoff)
    ready = validation["valid"] is True and validation["ready_for_executor_adapter"] is True

    request_steps = tuple(
        request["step"] for request in handoff.get("requests", ())
    ) if ready else ()

    return {
        "version": CODEX_EXECUTOR_ADAPTER_DESIGN_VERSION,
        "adapter_valid": validation["valid"] is True,
        "adapter_ready": ready,
        "provider": "codex",
        "mode": "design_only",
        "branch": handoff.get("branch") if ready else None,
        "request_steps": request_steps,
        "request_count": len(request_steps),
        "requires_future_activation_review": ready,
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


def validate_codex_executor_adapter_design():
    from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_handoff_boundary import (
        build_bounded_executor_handoff_boundary,
    )

    handoff = build_bounded_executor_handoff_boundary(cycles_completed=9, repair_attempts=1)
    design = build_codex_executor_adapter_design(handoff)
    assert design["adapter_valid"] is True
    assert design["adapter_ready"] is True
    assert design["provider"] == "codex"
    assert design["mode"] == "design_only"
    assert design["branch"] == "research-lab"
    assert design["request_count"] == 7
    assert design["requires_future_activation_review"] is True
    assert design["codex_invocation_authorized"] is False
    assert design["codex_invoked"] is False
    assert design["external_action_authorized"] is False

    blocked = build_codex_executor_adapter_design(None)
    assert blocked["adapter_valid"] is False
    assert blocked["adapter_ready"] is False
    assert blocked["request_steps"] == ()
    assert blocked["codex_invoked"] is False
    return True
