"""Autonomous research-cycle runner."""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(os.environ.get("WARASHIBE_LAB_OUTPUT", ROOT / "research_output"))
HISTORY_LIMIT = 120


def run_command(args):
    completed = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    return {"command": " ".join(args), "returncode": completed.returncode,
            "stdout": completed.stdout[-4000:], "stderr": completed.stderr[-4000:]}


def run_cycle():
    checks = [run_command([sys.executable, "-m", "research_lab.test_lab"]),
              run_command([sys.executable, "-m", "research_lab.test_storage"]),
              run_command([sys.executable, "-m", "research_lab.speed_experiment"]),
              run_command([sys.executable, "-m", "research_lab.transaction_cost_experiment"]),
              run_command([sys.executable, "-m", "research_lab.test_real_market"]),
              run_command([sys.executable, "-m", "research_lab.test_real_market_source"]),
              run_command([sys.executable, "-m", "research_lab.test_market_evidence"]),
              run_command([sys.executable, "-m", "research_lab.test_evidence_candidate_pipeline"]),
              run_command([sys.executable, "-m", "research_lab.test_real_market_route_bridge"]),
              run_command([sys.executable, "-m", "research_lab.test_route_evidence_uncertainty"]),
              run_command([sys.executable, "-m", "research_lab.test_calibrated_uncertainty"]),
              run_command([sys.executable, "-m", "research_lab.test_raw_outcome_calibration"]),
              run_command([sys.executable, "-m", "research_lab.test_posterior_route_integration"]),
              run_command([sys.executable, "-m", "research_lab.test_posterior_uncertainty_ranking"]),
              run_command([sys.executable, "-m", "research_lab.test_dashboard_kpis"]),
              run_command([sys.executable, "-m", "research_lab.test_dashboard_uncertainty"]),
              run_command([sys.executable, "-m", "research_lab.test_github_actions_bridge"])]
    passed = all(check["returncode"] == 0 for check in checks)
    snapshot = {"generated_at": datetime.now(timezone.utc).isoformat(),
                "status": "passed" if passed else "failed",
                "stage": "live_outcome_dashboard_bridge", "next_theme": "live_market_outcome_store", "checks": checks}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    history_path = OUTPUT / "history.json"
    try:
        history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.exists() else []
    except (OSError, json.JSONDecodeError):
        history = []
    history.append({"generated_at": snapshot["generated_at"], "status": snapshot["status"],
                    "stage": snapshot["stage"], "next_theme": snapshot["next_theme"],
                    "passed_checks": sum(1 for x in checks if x["returncode"] == 0),
                    "total_checks": len(checks)})
    history_path.write_text(json.dumps(history[-HISTORY_LIMIT:], ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT / "latest.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT / "latest.md").write_text("# Warashibe AI Lab — Latest Run\n\n"
        + f"- Generated: {snapshot['generated_at']}\n- Status: **{snapshot['status'].upper()}**\n"
        + f"- Stage: {snapshot['stage']}\n- Next theme: {snapshot['next_theme']}\n", encoding="utf-8")
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(run_cycle())
