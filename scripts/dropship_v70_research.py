"""Run one read-only v7 research cycle and write a sanitized evidence artifact."""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from dropship.real_runtime_sources import build_real_runtime_sources
from dropship.v70_research_orchestrator import research_v70

def sanitized_report(sources, *, capital_usd=None):
    if sources["status"] != "ready":
        return {"status": "setup_required", "reason": sources.get("reason"),
                "candidate_count": 0, "evidence_ready": False,
                "human_gate_ready": False, "live_execution_allowed": False}
    result = research_v70(
        sources["supplier_provider"], sources["market_provider"],
        max_candidates=5, max_market_queries=5, max_quotes=10,
        capital_usd=capital_usd,
    )
    selected = result["proposed_single_candidate"]
    return {
        "status": "observation_captured" if result["candidate_count"] else "no_candidates",
        "version": result["version"],
        "observed_at": result["observed_at"],
        "candidate_count": result["candidate_count"],
        "selected_candidate_reference": selected["candidate_id"] if selected else None,
        "missing_evidence": selected["unknown_fields"] if selected else [],
        "next_evidence_actions": result["next_evidence_actions"],
        "acceptance_status": result["acceptance_status"],
        "evidence_ready": False, "human_gate_ready": False,
        "live_execution_allowed": False,
    }

def main():
    output = Path(os.getenv("DROPSHIP_V70_EVIDENCE_PATH", "artifacts/v70-shadow-observation.json"))
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        report = sanitized_report(build_real_runtime_sources())
    except Exception as exc:
        # Do not write sensitive raw provider responses or credentials.
        report = {"status": "research_failed", "error_kind": type(exc).__name__,
                  "observed_at": datetime.now(timezone.utc).isoformat(),
                  "evidence_ready": False, "human_gate_ready": False,
                  "live_execution_allowed": False}
    output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    if report["status"] == "research_failed":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
