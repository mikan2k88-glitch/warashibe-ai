from __future__ import annotations


def assess_refund_recovery_readiness(payload: dict) -> dict:
    checks = {
        "refund_terms_known": payload.get("refund_terms_known") is True,
        "supplier_cancel_path_known": payload.get("supplier_cancel_path_known") is True,
        "customer_contact_path_known": payload.get("customer_contact_path_known") is True,
        "manual_intervention_available": payload.get("manual_intervention_available") is True,
        "automatic_refund_disabled": payload.get("automatic_refund_enabled") is not True,
        "automatic_cancel_disabled": payload.get("automatic_cancel_enabled") is not True,
    }
    passed = all(checks.values())
    return {
        "status": "refund_recovery_ready" if passed else "refund_recovery_incomplete",
        "passed": passed,
        "checks": checks,
        "automatic_refund_enabled": False,
        "automatic_cancel_enabled": False,
        "live_execution_allowed": False,
    }
