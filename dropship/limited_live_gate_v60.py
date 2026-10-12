from __future__ import annotations

from .approval_intent import build_approval_intent, validate_approval_intent
from .execution_receipt import build_execution_receipt
from .kill_switch import assess_kill_switch
from .live_preflight_audit import build_live_preflight_audit
from .one_shot_contract import build_one_shot_contract
from .recovery_plan_v58 import build_recovery_plan
from .transition_gate_v59 import assess_transition_gate


def build_v60_gate(review: dict) -> dict:
    preflight = build_live_preflight_audit(
        review,
        existing_idempotency_keys=[],
        limits={
            "max_orders": 1,
            "max_products": 1,
            "max_quantity_per_order": 1,
            "max_working_capital": 3000,
            "max_expected_loss": 3000,
        },
        kill_switch=False,
        recovery={
            "refund_terms_known": True,
            "supplier_cancel_path_known": True,
            "customer_contact_path_known": True,
            "manual_intervention_available": True,
            "automatic_refund_enabled": False,
            "automatic_cancel_enabled": False,
        },
    )

    intent = build_approval_intent(
        review,
        approval_id="v60-proof-approval",
        max_amount=min(
            3000.0,
            float((review.get("summary") or {}).get("required_working_capital") or 3000),
        ),
        expires_at="2099-12-31T23:59:59+00:00",
    )
    intent_validation = validate_approval_intent(intent, used_ids=[])
    contract = build_one_shot_contract(intent, preflight)
    receipt = build_execution_receipt(contract, result="not_executed")
    recovery = build_recovery_plan({
        "manual_contact_path": "human_operator",
        "supplier_cancel_path": "manual_supplier_contact",
        "refund_terms_known": True,
        "kill_switch_available": True,
        "support_owner": "human_operator",
    })
    kill = assess_kill_switch(explicit=False)
    transition = assess_transition_gate(
        contract=contract,
        receipt=receipt,
        recovery_plan=recovery,
        kill_switch_enabled=kill["enabled"],
    )

    checks = {
        "preflight_ready": preflight["ready_for_human_gate"] is True,
        "intent_valid": intent_validation["valid"] is True,
        "contract_ready": contract["status"] == "contract_ready",
        "recovery_ready": recovery["status"] == "recovery_plan_ready",
        "final_human_gate_ready": transition["ready"] is True,
        "not_executed": receipt["result"] == "not_executed",
        "external_write_not_performed": receipt["external_write_performed"] is False,
    }

    return {
        "gate_version": "6.0",
        "status": "limited_live_gate_ready" if all(checks.values()) else "blocked",
        "passed": all(checks.values()),
        "checks": checks,
        "preflight": preflight,
        "approval_intent": intent,
        "approval_validation": intent_validation,
        "contract": contract,
        "receipt": receipt,
        "recovery_plan": recovery,
        "transition_gate": transition,
        "human_gate_required": True,
        "automatic_execution": False,
        "external_write_enabled": False,
        "live_execution_allowed": False,
    }
