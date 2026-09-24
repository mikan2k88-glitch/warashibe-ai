"""Define the fail-closed boundary before any future real executor.

The boundary consumes validated local executor-contract data and emits only an
inert handoff description. No repository or external action is performed.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_executor_contract import (
    build_executor_contract,
)
from research_lab.autonomous_research_orchestrator_execution_layer_executor_contract_validation import (
    validate_executor_contract_result,
)

EXECUTION_LAYER_EXECUTOR_BOUNDARY_VERSION = "0.1"


def build_executor_boundary(cycles_completed=0, ci_status="success", repair_attempts=0):
    contract = build_executor_contract(cycles_completed, ci_status, repair_attempts)
    validation = validate_executor_contract_result(contract)
    boundary_open = validation["valid"] is True and validation["ready"] is True

    return {
        "version": EXECUTION_LAYER_EXECUTOR_BOUNDARY_VERSION,
        "boundary_valid": validation["valid"],
        "boundary_open": boundary_open,
        "handoff_requests": contract["requests"] if boundary_open else (),
        "handoff_count": contract["request_count"] if boundary_open else 0,
        "executor_invocation_authorized": False,
        "executor_invoked": False,
        "research_branch_only": True,
        "requires_human_gate_for_external_execution": True,
        "human_gate_required": boundary_open,
        "reason": "executor_boundary_human_gate" if boundary_open else validation["reason"],
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }


def validate_execution_layer_executor_boundary():
    ready = build_executor_boundary()
    assert ready["boundary_valid"] is True
    assert ready["boundary_open"] is True
    assert ready["human_gate_required"] is True
    assert ready["executor_invocation_authorized"] is False
    assert ready["executor_invoked"] is False
    assert ready["handoff_count"] == 7

    blocked = build_executor_boundary(ci_status="failure")
    assert blocked["boundary_valid"] is True
    assert blocked["boundary_open"] is False
    assert blocked["human_gate_required"] is False
    assert blocked["handoff_requests"] == ()
    return True
