from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json


def build_approval_intent(review: dict, *, approval_id: str, max_amount: float, expires_at: str) -> dict:
    body = {
        "intent_version": "5.5",
        "approval_id": str(approval_id),
        "product_key": str(review.get("product_key") or ""),
        "max_amount": float(max_amount),
        "expires_at": str(expires_at),
        "single_use": True,
        "human_gate_required": True,
        "external_write_enabled": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    raw = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    body["sha256"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return body


def validate_approval_intent(intent: dict, *, used_ids: list[str] | None = None) -> dict:
    used = str(intent.get("approval_id") or "") in set(used_ids or [])
    checks = {
        "approval_id_present": bool(intent.get("approval_id")),
        "product_key_present": bool(intent.get("product_key")),
        "positive_max_amount": float(intent.get("max_amount") or 0) > 0,
        "single_use": intent.get("single_use") is True,
        "not_used": not used,
        "external_write_disabled": intent.get("external_write_enabled") is False,
    }
    return {
        "valid": all(checks.values()),
        "checks": checks,
        "used": used,
        "external_write_enabled": False,
    }
