from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json

from .idempotency import reserve_idempotency
from .kill_switch import assess_kill_switch
from .limited_live_limits import assess_limited_live_limits
from .refund_recovery_readiness import assess_refund_recovery_readiness


def build_live_preflight_audit(
    review: dict,
    *,
    existing_idempotency_keys: list[str] | None = None,
    limits: dict | None = None,
    kill_switch: bool | None = None,
    recovery: dict | None = None,
) -> dict:
    summary = review.get("summary") or {}
    candidate = (review.get("review") or {}).get("candidate") or {}

    idempotency = reserve_idempotency({
        "customer_order_id": "future-single-order",
        "product_key": review.get("product_key"),
        "supplier": candidate.get("supplier"),
        "quantity": 1,
        "intent_type": "limited_live_preparation",
    }, existing_idempotency_keys or [])

    limit_result = assess_limited_live_limits({
        "order_count": 1,
        "product_count": 1,
        "quantity": 1,
        "required_working_capital": summary.get("required_working_capital") or 0,
        "expected_max_loss": float(summary.get("required_working_capital") or 0),
    }, limits)

    kill = assess_kill_switch(explicit=kill_switch)
    recovery_result = assess_refund_recovery_readiness(recovery or {})

    checks = {
        "promotion_review_ready": review.get("eligible_for_human_review") is True,
        "idempotency_reserved": idempotency["reserved"] is True,
        "limits_passed": limit_result["passed"] is True,
        "kill_switch_clear": kill["enabled"] is False,
        "refund_recovery_ready": recovery_result["passed"] is True,
    }
    ready = all(checks.values())

    body = {
        "audit_version": "5.4",
        "product_key": review.get("product_key"),
        "checks": checks,
        "idempotency": idempotency,
        "limits": limit_result,
        "kill_switch": kill,
        "refund_recovery": recovery_result,
        "ready_for_human_gate": ready,
        "human_gate_required": True,
        "limited_live_execution_enabled": False,
        "live_execution_allowed": False,
        "observed_at": datetime.now(timezone.utc).isoformat(),
    }
    raw = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    body["sha256"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return body
