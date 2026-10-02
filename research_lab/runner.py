"""Build-first autonomous research-cycle runner.

The default cycle intentionally runs a small, high-signal test profile.
Broader regression remains available explicitly via WARASHIBE_LAB_PROFILE.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(os.environ.get("WARASHIBE_LAB_OUTPUT", ROOT / "research_output"))
HISTORY_LIMIT = 120

PROFILES = {
    "build": [
        "research_lab.test_product_policy_bridge",
        "research_lab.test_product_start_capital",
        "research_lab.test_product_capital_policy",
        "research_lab.test_human_review_api",
        "research_lab.test_dry_run_commerce_plan",
        "research_lab.test_commerce_economics",
        "research_lab.test_history_dashboard_api",
        "research_lab.test_preflight_safety_gate",
        "research_lab.test_human_pilot_session",
        "research_lab.test_purchase_intent",
        "research_lab.test_commerce_adapter_sandbox",
        "research_lab.test_live_readiness_audit",
        "research_lab.test_problem_repair_candidate",
        "research_lab.test_problem_repair_plan",
        "research_lab.test_problem_repair_ai_decision",
        "research_lab.test_problem_repair_execution_boundary",
        "research_lab.test_problem_repair_validation_gate",
        "research_lab.test_problem_repair_cycle",
        "research_lab.test_problem_repair_pipeline",
        "research_lab.test_repair_execution_controller",
        "research_lab.test_hourly_research_scheduler_contract",
        "research_lab.test_scheduler_live_connector",
    ],
    "scheduler": [
        "research_lab.test_hourly_research_scheduler_contract",
        "research_lab.test_scheduler_live_connector",
        "research_lab.test_scheduler_connector_verification",
        "research_lab.test_scheduler_connector_evidence_bridge",
        "research_lab.test_scheduler_connector_live_probe_contract",
        "research_lab.test_scheduler_connector_milestone_checkpoint",
        "research_lab.test_scheduler_trigger_milestone_record",
    ],
    "repair": [
        "research_lab.test_problem_guardrail_candidate",
        "research_lab.test_problem_guardrail_recurrence",
        "research_lab.test_problem_repair_candidate",
        "research_lab.test_problem_repair_plan",
        "research_lab.test_problem_repair_ai_decision",
        "research_lab.test_problem_repair_execution_boundary",
        "research_lab.test_problem_repair_validation_gate",
        "research_lab.test_problem_repair_audit_record",
        "research_lab.test_problem_repair_ledger",
        "research_lab.test_problem_repair_cycle",
        "research_lab.test_problem_repair_pipeline",
        "research_lab.test_repair_execution_controller",
    ],
    "core": [
        "research_lab.test_warashibe_core_mode",
        "research_lab.test_real_world_engine",
        "research_lab.test_real_world_api",
        "research_lab.test_real_world_dry_run_pipeline",
        "research_lab.test_real_world_policy_bridge",
        "research_lab.test_real_world_route_bridge",
    ],
}


def decide_runner_handoff(event, passed, profile):
    if not passed:
        return {
            "stage": "targeted_checks_failed",
            "next_action": "repair_current_problem",
            "decision_reason": "targeted_checks_failed",
        }
    if event == "schedule":
        return {
            "stage": "repair_cycle_ready",
            "next_action": "finalize_bounded_repair_cycle",
            "decision_reason": "scheduled_repair_pipeline_passed",
            "repair_pipeline": {
                "candidate": "ready",
                "ai_decision": "required",
                "execution_boundary": "enforced",
                "exact_sha_validation": "required",
                "audit_ledger": "required",
            },
        }
    return {
        "stage": "targeted_checks_passed",
        "next_action": "continue_current_problem",
        "decision_reason": f"{profile}_profile_passed",
        "repair_pipeline": {
            "candidate": "ready",
            "ai_decision": "required",
            "execution_boundary": "enforced",
            "exact_sha_validation": "required",
            "audit_ledger": "required",
        } if profile in {"build", "repair"} else None,
    }


def run_command(args):
    completed = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    return {
        "command": " ".join(args),
        "returncode": completed.returncode,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
    }


def selected_modules():
    profile = os.environ.get("WARASHIBE_LAB_PROFILE", "build").strip().lower()
    modules = PROFILES.get(profile)
    if modules is None:
        return "invalid", []
    return profile, modules


def run_cycle():
    profile, modules = selected_modules()
    if not modules:
        print(json.dumps({"status": "failed", "reason": "unknown_test_profile", "profile": profile}))
        return 2

    checks = [run_command([sys.executable, "-m", module]) for module in modules]
    passed = all(check["returncode"] == 0 for check in checks)
    handoff = decide_runner_handoff(os.environ.get("GITHUB_EVENT_NAME"), passed, profile)
    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if passed else "failed",
        "profile": profile,
        "head_sha": os.environ.get("GITHUB_SHA"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        **handoff,
        "checks": checks,
    }

    OUTPUT.mkdir(parents=True, exist_ok=True)
    history_path = OUTPUT / "history.json"
    try:
        history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.exists() else []
    except (OSError, json.JSONDecodeError):
        history = []

    history.append({
        "generated_at": snapshot["generated_at"],
        "status": snapshot["status"],
        "profile": profile,
        "stage": snapshot["stage"],
        "next_action": snapshot["next_action"],
        "decision_reason": snapshot["decision_reason"],
        "passed_checks": sum(1 for item in checks if item["returncode"] == 0),
        "total_checks": len(checks),
    })
    history_path.write_text(
        json.dumps(history[-HISTORY_LIMIT:], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUTPUT / "latest.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUTPUT / "latest.md").write_text(
        "# Warashibe AI Lab — Latest Run\n\n"
        + f"- Generated: {snapshot['generated_at']}\n"
        + f"- Status: **{snapshot['status'].upper()}**\n"
        + f"- Profile: {profile}\n"
        + f"- Stage: {snapshot['stage']}\n"
        + f"- Next action: {snapshot['next_action']}\n",
        encoding="utf-8",
    )
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(run_cycle())
