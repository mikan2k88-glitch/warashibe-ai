from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json


def create_audit_record(event_type: str, payload: dict) -> dict:
    body = {
        "event_type": str(event_type),
        "payload": dict(payload),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    digest_source = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    body["sha256"] = hashlib.sha256(digest_source.encode("utf-8")).hexdigest()
    body["append_only_intent"] = True
    return body
