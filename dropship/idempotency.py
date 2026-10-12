from __future__ import annotations

import hashlib
import json


def build_idempotency_key(payload: dict) -> str:
    stable = {
        "customer_order_id": str(payload.get("customer_order_id") or ""),
        "product_key": str(payload.get("product_key") or ""),
        "supplier": str(payload.get("supplier") or ""),
        "quantity": int(payload.get("quantity") or 1),
        "intent_type": str(payload.get("intent_type") or "limited_live_preparation"),
    }
    raw = json.dumps(stable, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def reserve_idempotency(payload: dict, existing_keys: list[str]) -> dict:
    key = build_idempotency_key(payload)
    duplicate = key in set(existing_keys or [])
    return {
        "idempotency_key": key,
        "reserved": not duplicate,
        "duplicate": duplicate,
        "automatic_retry_allowed": False,
        "live_execution_allowed": False,
    }
