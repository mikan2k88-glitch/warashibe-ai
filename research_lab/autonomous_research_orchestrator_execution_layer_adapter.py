"""Adapt a validated cycle plan into inert executor requests.

The adapter creates local request data only. It never invokes GitHub, network,
credentials, production, commerce, or notification systems.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_cycle_plan import (
    build_execution_cycle_plan,
)

EXECUTION_LAYER_ADAPTER_VERSION = "0.1"


def build_execution_adapter(cycles_completed=0, ci_status="success", repair_attempts=0):
    plan = build_execution_cycle_plan(
        cycles_completed=cycles_completed,
        ci_status=ci_status,
        repair_attempts=repair_attempts,
    )
    ready = plan["ready_for_execution_adapter"] is True
    requests = tuple(
        {
            "step": step,
            "requested": ready,
            "performed": False,
            "external_action_authorized": False,
        }
        for step in plan["planned_steps"]
    ) if ready else ()

    return {
        "version": EXECUTION_LAYER_ADAPTER_VERSION,
        "adapter_valid": plan["plan_valid"] is True,
        "ready": ready,
        "requests": requests,
        "request_count": len(requests),
        "human_gate_required": plan["human_gate_required"],
        "stop_reason": plan["stop_reason"],
        "research_branch_only": True,
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }


def validate_execution_layer_adapter():
    adapter = build_execution_adapter()
    assert adapter["adapter_valid"] is True
    assert adapter["ready"] is True
    assert adapter["request_count"] == 7
    assert all(request["performed"] is False for request in adapter["requests"])
    assert all(request["external_action_authorized"] is False for request in adapter["requests"])

    blocked = build_execution_adapter(ci_status="failure")
    assert blocked["adapter_valid"] is True
    assert blocked["ready"] is False
    assert blocked["requests"] == ()
    assert blocked["external_action_performed"] is False
    return True
