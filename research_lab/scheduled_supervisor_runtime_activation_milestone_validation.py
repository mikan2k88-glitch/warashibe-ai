"""Milestone validation for scheduled GPT Supervisor runtime activation.

Validates the designed activation path:
readiness -> connector review -> activation gate -> execution plan -> receipt.

This module performs no live activation or external action.
"""

from research_lab.scheduled_supervisor_runtime_activation_review import (
    build_runtime_readiness_snapshot,
)
from research_lab.scheduled_supervisor_runtime_live_connector_design import (
    build_connector_status,
)
from research_lab.scheduled_supervisor_runtime_connector_activation_review import (
    review_connector_activation,
)
from research_lab.scheduled_supervisor_runtime_activation_gate_design import (
    build_activation_gate_snapshot,
    evaluate_activation_gate,
)
from research_lab.scheduled_supervisor_runtime_activation_execution_design import (
    build_activation_execution_plan,
    evaluate_activation_step,
)
from research_lab.scheduled_supervisor_runtime_activation_receipt_design import (
    build_activation_receipt,
    validate_activation_receipt,
)

SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_MILESTONE_VERSION = "0.1"


def _verified(name):
    return build_connector_status(
        name=name,
        state="verified",
        configuration_present=True,
        transport_ready=True,
        authentication_ready=True,
        healthcheck_passed=True,
        policy_ready=True,
    )


def validate_scheduled_runtime_activation_milestone():
    readiness = build_runtime_readiness_snapshot()

    scheduler = _verified("scheduler")
    gemini = _verified("gemini")
    codex = _verified("codex")

    connector_review = review_connector_activation(
        scheduler,
        gemini,
        codex,
    )

    gate_snapshot = build_activation_gate_snapshot(
        live_scheduler_connected=True,
        live_gemini_connected=True,
        live_codex_connected=True,
        explicit_human_approval=True,
    )
    gate_result = evaluate_activation_gate(gate_snapshot)

    plan = build_activation_execution_plan(
        gate_result,
        connector_review,
    )

    plan_complete = evaluate_activation_step(
        plan,
        completed_steps=plan.get("steps", ()),
    )

    receipt = build_activation_receipt(
        activation_id="activation-milestone-001",
        started_at="2026-09-25T19:00:00+09:00",
        completed_at="2026-09-25T19:01:00+09:00",
        completed_steps=plan.get("steps", ()),
        scheduler_connected=True,
        gemini_connected=True,
        codex_connected=True,
        runtime_state="idle",
    )
    receipt_validation = validate_activation_receipt(receipt)

    checks = {
        "design_readiness_green": readiness["design_ready"] is True,
        "connectors_ready": (
            connector_review["ready_for_activation_gate"] is True
        ),
        "activation_gate_clear": gate_result["approved"] is True,
        "execution_plan_valid": plan["valid"] is True,
        "activation_sequence_complete": (
            plan_complete["action"] == "activation_sequence_complete"
        ),
        "receipt_confirms_runtime": (
            receipt_validation["runtime_activation_confirmed"] is True
        ),
        "receipt_is_not_authority": (
            receipt_validation["external_action_authorized"] is False
        ),
    }

    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_MILESTONE_VERSION,
        "milestone": "scheduled_supervisor_runtime_activation",
        "passed": all(checks.values()),
        "checks": checks,
        "validated_path": (
            "runtime_readiness",
            "connector_review",
            "activation_gate",
            "activation_execution_plan",
            "activation_receipt",
        ),
        "design_only": True,
        "live_activation_performed": False,
        "external_action_authorized": False,
    }


def validate_scheduled_supervisor_runtime_activation_milestone_validation():
    report = validate_scheduled_runtime_activation_milestone()
    assert report["passed"] is True
    assert report["design_only"] is True
    assert report["live_activation_performed"] is False
    assert report["external_action_authorized"] is False
    return True
