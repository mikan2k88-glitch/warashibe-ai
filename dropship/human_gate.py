from __future__ import annotations

APPROVAL_CODE = "8888"


def prepare_human_gate_package(context: dict) -> dict:
    return {
        "status": "human_gate_package_ready",
        "selected_product_key": context.get("selected_product_key"),
        "expected_net_profit": context.get("expected_net_profit"),
        "required_working_capital": context.get("required_working_capital"),
        "supplier": context.get("supplier"),
        "evidence": dict(context.get("evidence") or {}),
        "approval_required": True,
        "approval_code_required": True,
        "live_execution_allowed": False,
    }


def verify_human_approval(code: str) -> dict:
    approved = str(code) == APPROVAL_CODE
    return {
        "approved": approved,
        "status": "approval_verified" if approved else "approval_rejected",
        "live_execution_allowed": False,
        "reason": "approval alone does not enable live commerce in v1.0",
    }
