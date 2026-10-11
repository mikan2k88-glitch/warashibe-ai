from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json


def build_research_run_record(result: dict, *, mode: str) -> dict:
    ranking = result.get("ranking") or {}
    best = ranking.get("best") or {}
    body = {
        "run_version": "1.0",
        "mode": str(mode),
        "supplier_provider": result.get("supplier_provider"),
        "market_provider": result.get("market_provider"),
        "supplier_candidate_count": int(result.get("supplier_candidate_count") or 0),
        "market_query_count": int(result.get("market_query_count") or 0),
        "market_cache_hits": int(result.get("market_cache_hits") or 0),
        "error_count": len(result.get("errors") or []),
        "best_product_key": best.get("product_key"),
        "best_opportunity_score": float(best.get("opportunity_score") or 0),
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "commerce_external_writes": False,
        "live_execution_allowed": False,
    }
    raw = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    body["sha256"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    body["append_only_intent"] = True
    return body
