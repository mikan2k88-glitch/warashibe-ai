"""Operator-invoked read-only research run; no scheduled commerce writes."""
import json
from dropship.real_runtime_sources import build_real_runtime_sources
from dropship.v70_research_orchestrator import research_v70

def main():
    try:
        sources = build_real_runtime_sources()
        if sources["status"] != "ready":
            print(json.dumps({"status": "setup_required", "reason": sources.get("reason"),
                              "live_execution_allowed": False}))
            return
        result = research_v70(sources["supplier_provider"], sources["market_provider"],
                              max_candidates=5, max_market_queries=5, max_quotes=10)
        # Research only: sanitized summary, no credentials or unrestricted payloads.
        print(json.dumps({
            "version": result["version"], "candidate_count": result["candidate_count"],
            "acceptance_status": result["acceptance_status"],
            "unknown_fields": result["proposed_single_candidate"]["unknown_fields"]
                              if result["proposed_single_candidate"] else [],
            "human_gate_ready": False, "live_execution_allowed": False,
        }))
    except Exception as exc:
        print(json.dumps({"status": "research_failed", "error_kind": type(exc).__name__,
                          "human_gate_ready": False, "live_execution_allowed": False}))
        raise SystemExit(1)

if __name__ == "__main__":
    main()
