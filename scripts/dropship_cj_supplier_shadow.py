from __future__ import annotations

import json
import os

from dropship.cj_only_collector import run_cj_supplier_collection
from dropship.cj_runtime_source import build_cj_runtime_source
from dropship.persistence_health import assess_persistence_environment
from dropship.supabase_rest import SupabaseRestClient


def main():
    source = build_cj_runtime_source()
    persistence = assess_persistence_environment()

    if source["status"] != "ready":
        print(json.dumps({
            "status": "setup_required",
            "reason": source["reason"],
            "token_readiness": source["token_readiness"],
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

    result = run_cj_supplier_collection(
        source["supplier_provider"],
        persistence_client=SupabaseRestClient(),
        max_items=int(os.environ.get("DROPSHIP_CJ_SHADOW_MAX_ITEMS", "20")),
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))

    if result["live_execution_allowed"]:
        raise SystemExit("live execution must remain disabled")
    if result["status"] == "provider_read_failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
