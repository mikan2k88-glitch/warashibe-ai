from __future__ import annotations


def build_one_shot_contract(intent: dict, preflight: dict) -> dict:
    checks = {
        "intent_valid": bool(intent.get("sha256")),
        "preflight_ready": preflight.get("ready_for_human_gate") is True,
        "single_use": intent.get("single_use") is True,
        "human_gate_required": intent.get("human_gate_required") is True,
    }
    ready = all(checks.values())
    return {
        "contract_version": "5.6",
        "status": "contract_ready" if ready else "blocked",
        "checks": checks,
        "approval_id": intent.get("approval_id"),
        "product_key": intent.get("product_key"),
        "max_amount": intent.get("max_amount"),
        "single_use": True,
        "external_write_enabled": False,
        "automatic_retry_allowed": False,
    }
