from __future__ import annotations


def build_recovery_plan(context: dict) -> dict:
    checks = {
        "manual_contact_path": bool(context.get("manual_contact_path")),
        "supplier_cancel_path": bool(context.get("supplier_cancel_path")),
        "refund_terms_known": context.get("refund_terms_known") is True,
        "kill_switch_available": context.get("kill_switch_available") is True,
        "support_owner_assigned": bool(context.get("support_owner")),
    }
    ready = all(checks.values())
    return {
        "plan_version": "5.8",
        "status": "recovery_plan_ready" if ready else "recovery_plan_incomplete",
        "checks": checks,
        "manual_only": True,
        "automatic_cancel_enabled": False,
        "automatic_refund_enabled": False,
        "external_write_enabled": False,
    }
