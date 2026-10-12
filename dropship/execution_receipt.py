from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json


def build_execution_receipt(contract: dict, *, result: str = "not_executed") -> dict:
    body = {
        "receipt_version": "5.7",
        "approval_id": contract.get("approval_id"),
        "product_key": contract.get("product_key"),
        "result": str(result),
        "external_write_performed": False,
        "payment_captured": False,
        "supplier_order_created": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    raw = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    body["sha256"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return body
