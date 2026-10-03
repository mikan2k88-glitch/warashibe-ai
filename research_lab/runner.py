"""Build-first autonomous research-cycle runner.

The default cycle intentionally runs a small, high-signal test profile.
Broader regression remains available explicitly via WARASHIBE_LAB_PROFILE.
Scheduled cycles are routed through the Warashibe HQ priority program.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from research_lab.hq_development_program import build_hq_development_program

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
        "research_lab.test_human_go_no_go",
        "research_lab.test_live_pilot_guard",
        "research_lab.test_live_commerce_adapter",
        "research_lab.test_single_purchase_execution",
        "research_lab.test_purchase_receipt_reconciliation",
        "research_lab.test_receive_inspection",
        "research_lab.test_sale_plan",
        "research_lab.test_human_sale_decision",
        "research_lab.test_limited_sale_execution",
        "research_lab.test_trade_settlement",
        "research_lab.test_one_cycle_warashibe_proof",
        "research_lab.test_live_pilot_review",
        "research_lab.test_runtime_status",
        "research_lab.test_headquarters",
        "research_lab.test_hq_development_program",
        "research_lab.test_hq_runner_integration",
        "research_lab.test_hq_dashboard",
        "research_lab.test_supabase_strategy_decision_repository",
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
        "research_lab.test_hq_development_program",
        "research_lab.test_hq_runner_integration",
        "research_lab.test_hq_dashboard",
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


def _env_flag(name, default=False):
    raw = os.environ.get(name)
    if raw is None:
        return bool(default)
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def current_hq_operational_evidence():
    return {
        "hq_runner_integrated": True,
        "real_pilot_decision_packet_ready": _env_flag(
            "WARASHIBE_REAL_PILOT_PACKET_READY"
        ),
        "ceo_approval_gate_ready": _env_flag("WARASHIBE_CEO_APPROVAL_GATE_READY"),
        "live_pilot_verified": _env_flag("WARASHIBE_LIVE_PILOT_VERIFIED"),
        "learning_feedback_ingested": _env_flag(
            "WARASHIBE_LEARNING_FEEDBACK_INGESTED"
        ),
        "capital_velocity_optimized": _env_flag(
            "WARASHIBE_CAPITAL_VELOCITY_OPTIMIZED"
        ),
        "controlled_automation_scope_ready": _env_flag(
            "WARASHIBE_CONTROLLED_AUTOMATION_SCOPE_READY"
        ),
    }


def build_hq_runner_handoff(event, passed, profile, operational_evidence=None):
    if not passed:
        return {
            "stage": "targeted_checks_failed",
            "next_action": "repair_current_problem",
            "decision_reason": "targeted_checks_failed",
            "human_gate_preserved": True,
            "external_execution_authorized": False,
        }

    evidence = (
        dict(operational_evidence)
        if operational_evidence is not None
        else current_hq_operational_evidence()
    )
    program = build_hq_development_program(operational_evidence=evidence)
    selected = program.get("selected_operational_priority")
    selected_row = next(
        (
            row
            for row in program["operational_progress"]
            if row["priority"] == selected
        ),
        None,
    )

    if event == "schedule":
        if selected_row is None:
            return {
                "stage": "hq_program_operational_endpoint",
                "next_action": "strategy_review",
                "decision_reason": "all_operational_priorities_complete",
                "selected_priority": None,
                "hq_program": program,
                "human_gate_preserved": True,
                "external_execution_authorized": False,
            }
        objective = selected_row["objective"]
        return {
            "stage": "hq_priority_selected",
            "next_action": f"execute_{objective}",
            "decision_reason": f"hq_selected_{selected.lower()}",
            "selected_priority": selected,
            "selected_objective": objective,
            "hq_program": program,
            "human_gate_preserved": True,
            "external_execution_authorized": False,
        }

    return {
        "stage": "targeted_checks_passed",
        "next_action": (
            f"continue_{selected_row['objective']}"
            if selected_row is not None
            else "strategy_review"
        ),
        "decision_reason": f"{profile}_profile_passed_hq_reviewed",
        "selected_priority": selected,
        "selected_objective": (
            selected_row["objective"] if selected_row is not None else None
        ),
        "hq_program": program,
        "repair_pipeline": {
            "candidate": "ready",
            "ai_decision": "required",
            "execution_boundary": "enforced",
            "exact_sha_validation": "required",
            "audit_ledger": "required",
        }
        if profile in {"build", "repair"}
        else None,
        "human_gate_preserved": True,
        "external_execution_authorized": False,
    }


def decide_runner_handoff(event, passed, profile):
    return build_hq_runner_handoff(event, passed, profile)


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
        print(
            json.dumps(
                {
                    "status": "failed",
                    "reason": "unknown_test_profile",
                    "profile": profile,
                }
            )
        )
        return 2

    checks = [run_command([sys.executable, "-m", module]) for module in modules]
    passed = all(check["returncode"] == 0 for check in checks)
    handoff = build_hq_runner_handoff(
        os.environ.get("GITHUB_EVENT_NAME"),
        passed,
        profile,
    )
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
        history = (
            json.loads(history_path.read_text(encoding="utf-8"))
            if history_path.exists()
            else []
        )
    except (OSError, json.JSONDecodeError):
        history = []

    history.append(
        {
            "generated_at": snapshot["generated_at"],
            "status": snapshot["status"],
            "profile": profile,
            "stage": snapshot["stage"],
            "next_action": snapshot["next_action"],
            "decision_reason": snapshot["decision_reason"],
            "selected_priority": snapshot.get("selected_priority"),
            "passed_checks": sum(
                1 for item in checks if item["returncode"] == 0
            ),
            "total_checks": len(checks),
        }
    )
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
        + f"- Selected priority: {snapshot.get('selected_priority')}\n"
        + f"- Next action: {snapshot['next_action']}\n",
        encoding="utf-8",
    )
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(run_cycle())
