from __future__ import annotations


def assess_transition_gate(
    *,
    contract: dict,
    receipt: dict,
    recovery_plan: dict,
    kill_switch_enabled: bool,
) -> dict:
    checks = {
        "contract_ready": contract.get("status") == "contract_ready",
        "single_use_contract": contract.get("single_use") is True,
        "receipt_not_executed": receipt.get("result") == "not_executed",
        "recovery_ready": recovery_plan.get("status") == "recovery_plan_ready",
        "kill_switch_clear": kill_switch_enabled is False,
        "external_write_disabled": contract.get("external_write_enabled") is False,
    }
    ready = all(checks.values())
    return {
        "gate_version": "5.9",
        "status": "ready_for_final_human_gate" if ready else "blocked",
        "ready": ready,
        "checks": checks,
        "allowed_next_action": "final_human_review" if ready else "resolve_gate_failures",
        "automatic_transition": False,
        "external_write_enabled": False,
    }
