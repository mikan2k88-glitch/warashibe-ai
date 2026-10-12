from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json


def build_research_snapshot(payload: dict) -> dict:
    body = {
        "snapshot_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "maturity_stage": str(payload.get("maturity_stage") or "research"),
        "candidate_count": int(payload.get("candidate_count") or 0),
        "eligible_count": int(payload.get("eligible_count") or 0),
        "shadow_observations": int(payload.get("shadow_observations") or 0),
        "shadow_days": int(payload.get("shadow_days") or 0),
        "sandbox_cycles": int(payload.get("sandbox_cycles") or 0),
        "selected_product_key": payload.get("selected_product_key"),
        "estimated_net_profit": float(payload.get("estimated_net_profit") or 0),
        "external_writes": False,
        "live_execution_allowed": False,
    }
    raw = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    body["sha256"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    body["append_only_intent"] = True
    return body
