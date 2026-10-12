from __future__ import annotations

import json
import os

from dropship.actual_evidence_controller_v64 import run_actual_evidence_controller_v64
from dropship.persistence_health import assess_persistence_environment
from dropship.provider_handshake import run_provider_handshake
from dropship.real_runtime_sources import build_real_runtime_sources
from dropship.supabase_rest import SupabaseRestClient


def main():
    sources = build_real_runtime_sources()
    persistence = assess_persistence_environment()

    if sources["status"] != "ready":
        print(json.dumps({
            "status": "setup_required",
            "reason": sources["reason"],
            "token_readiness": sources["token_readiness"],
            "live_execution_allowed": False,
        }, ensure_ascii=False, sort_keys=True))
        return

    if persistence["status"] != "ready":
        print(json.dumps({
            "status": "setup_required",
            "reason": "supabase_persistence_not_configured",
            "persistence": persistence,
            "live_execution_allowed": False,
        }, ensure_ascii=False, sort_keys=True))
        return

    handshake = run_provider_handshake()
    if handshake["status"] != "real_provider_handshake_ready":
        print(json.dumps({
            "status": "setup_required",
            "reason": "provider_handshake_failed",
            "provider_handshake": handshake,
            "live_execution_allowed": False,
        }, ensure_ascii=False, sort_keys=True))
        raise SystemExit(1)

    client = SupabaseRestClient()
    result = run_actual_evidence_controller_v64(
        sources["supplier_provider"],
        sources["market_provider"],
        persistence_client=client,
        provider_handshake=handshake,
        available_capital=float(os.environ.get("DROPSHIP_AVAILABLE_CAPITAL", "3000")),
        supplier_currency=os.environ.get("DROPSHIP_SUPPLIER_CURRENCY", "USD"),
        target_currency=os.environ.get("DROPSHIP_TARGET_CURRENCY", "USD"),
        budget={
            "max_supplier_items": int(os.environ.get("DROPSHIP_MAX_SUPPLIER_ITEMS", "5")),
            "max_market_queries": int(os.environ.get("DROPSHIP_MAX_MARKET_QUERIES", "5")),
            "max_market_quotes_per_query": int(os.environ.get("DROPSHIP_MAX_QUOTES", "10")),
        },
        shadow_thresholds={
            "min_observations": int(os.environ.get("DROPSHIP_SHADOW_MIN_OBSERVATIONS", "20")),
            "min_observation_days": int(os.environ.get("DROPSHIP_SHADOW_MIN_DAYS", "7")),
        },
    )

    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if result["live_execution_allowed"]:
        raise SystemExit("live execution must remain disabled")


if __name__ == "__main__":
    main()
