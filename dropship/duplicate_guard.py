from __future__ import annotations

import hashlib
import json


def build_order_fingerprint(payload: dict) -> str:
    stable = {
        "customer_order_id": str(payload.get("customer_order_id") or ""),
        "product_key": str(payload.get("product_key") or ""),
        "supplier": str(payload.get("supplier") or ""),
        "quantity": int(payload.get("quantity") or 1),
    }
    raw = json.dumps(stable, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def assess_duplicate_order(payload: dict, existing_fingerprints: list[str]) -> dict:
    fingerprint = build_order_fingerprint(payload)
    duplicate = fingerprint in set(existing_fingerprints or [])
    return {
        "fingerprint": fingerprint,
        "duplicate": duplicate,
        "allowed": not duplicate,
        "live_action": False,
    }
