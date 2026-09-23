"""Autonomous research-cycle runner."""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(os.environ.get("WARASHIBE_LAB_OUTPUT", ROOT / "research_output"))


def run_command(args):
    completed = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    return {"command": " ".join(args), "returncode": completed.returncode,
            "stdout": completed.stdout[-4000:], "stderr": completed.stderr[-4000:]}


def run_cycle():
    checks = [run_command([sys.executable, "-m", "research_lab.test_lab"]),
              run_command([sys.executable, "-m", "research_lab.test_storage"]),
              run_command([sys.executable, "-m", "research_lab.speed_experiment"]),
              run_command([sys.executable, "-m", "research_lab.transaction_cost_experiment"])]
    passed = all(check["returncode"] == 0 for check in checks)
    snapshot = {"generated_at": datetime.now(timezone.utc).isoformat(),
                "status": "passed" if passed else "failed",
                "stage": "transaction_costs", "next_theme": "real_market_schema", "checks": checks}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "latest.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT / "latest.md").write_text("# Warashibe AI Lab — Latest Run\n\n"
        + f"- Generated: {snapshot['generated_at']}\n- Status: **{snapshot['status'].upper()}**\n"
        + f"- Stage: {snapshot['stage']}\n- Next theme: {snapshot['next_theme']}\n", encoding="utf-8")
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(run_cycle())
