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
    modules = [
        "research_lab.test_lab", "research_lab.test_storage", "research_lab.speed_experiment",
        "research_lab.transaction_cost_experiment", "research_lab.test_real_market",
        "research_lab.test_real_market_source", "research_lab.test_market_evidence",
        "research_lab.test_evidence_candidate_pipeline", "research_lab.test_real_market_route_bridge",
        "research_lab.test_route_evidence_uncertainty", "research_lab.test_calibrated_uncertainty",
        "research_lab.test_raw_outcome_calibration", "research_lab.test_posterior_route_integration",
        "research_lab.test_posterior_uncertainty_ranking", "research_lab.test_dashboard_kpis",
        "research_lab.test_dashboard_uncertainty", "research_lab.test_github_actions_bridge",
        "research_lab.test_live_outcome_store", "research_lab.test_persisted_outcome_posterior_bridge",
        "research_lab.test_persisted_posterior_uncertainty_ranking", "research_lab.test_outcome_learning_loop",
        "research_lab.test_outcome_repository", "research_lab.test_supabase_outcome_repository",
        "research_lab.test_outcome_repository_factory", "research_lab.test_repository_learning_loop_injection",
        "research_lab.test_repository_observability", "research_lab.test_live_market_evidence_ingestion",
        "research_lab.test_market_provider_contract", "research_lab.test_provider_ingestion_pipeline",
        "research_lab.test_evidence_grouping", "research_lab.test_market_identity_resolution",
        "research_lab.test_identity_aware_evidence_grouping", "research_lab.test_identifier_validation",
        "research_lab.test_validated_identity_resolution", "research_lab.test_isbn_identifier_validation",
        "research_lab.test_identifier_conflict_resolution", "research_lab.test_conflict_aware_evidence_grouping", "research_lab.test_market_estimate_quality_gate", "research_lab.test_quality_gated_candidate_pipeline", "research_lab.test_end_to_end_market_decision_pipeline", "research_lab.test_multi_provider_market_snapshot",
        "research_lab.test_multi_provider_decision_pipeline", "research_lab.test_market_snapshot_freshness", "research_lab.test_freshness_gated_multi_provider_decision", "research_lab.test_decision_outcome_learning_bridge", "research_lab.test_closed_loop_market_learning_cycle", "research_lab.test_closed_loop_observability", "research_lab.test_ebay_browse_adapter", "research_lab.test_ebay_browse_transport", "research_lab.test_ebay_browse_response_mapping", "research_lab.test_ebay_browse_ingestion_bridge", "research_lab.test_supabase_runtime_smoke", "research_lab.test_supabase_keepalive_scheduler", "research_lab.test_supabase_schema_contract", "research_lab.test_supabase_schema_migration_plan", "research_lab.test_supabase_schema_sql_rendering", "research_lab.test_supabase_schema_policy_contract", "research_lab.test_supabase_client_integration_design", "research_lab.test_supabase_schema_dry_run_validation", "research_lab.test_supabase_migration_readiness_gate", "research_lab.test_supabase_migration_approval_artifact", "research_lab.test_supabase_migration_preflight_report", "research_lab.test_autonomous_research_orchestrator_design", "research_lab.test_autonomous_research_state_machine", "research_lab.test_autonomous_research_cycle_budget", "research_lab.test_autonomous_research_decision_record", "research_lab.test_autonomous_research_cycle_plan", "research_lab.test_autonomous_research_policy_alignment", "research_lab.test_autonomous_research_execution_plan", "research_lab.test_autonomous_research_execution_receipt", "research_lab.test_autonomous_research_cycle_audit", "research_lab.test_autonomous_research_cycle_summary", "research_lab.test_autonomous_research_notification_policy", "research_lab.test_autonomous_research_cycle_report", "research_lab.test_autonomous_research_end_to_end_cycle", "research_lab.test_autonomous_research_runner_integration", "research_lab.test_autonomous_research_runner_snapshot_bridge", "research_lab.test_autonomous_research_snapshot_file_adapter", "research_lab.test_autonomous_research_snapshot_freshness_gate", "research_lab.test_autonomous_research_fresh_snapshot_decision", "research_lab.test_autonomous_research_safe_snapshot_controller", "research_lab.test_autonomous_research_controller_contract", "research_lab.test_autonomous_research_controller_policy_bridge", "research_lab.test_autonomous_research_controller_policy_enforcement", "research_lab.test_autonomous_research_controller_policy_guard", "research_lab.test_autonomous_research_controller_budget_guard", "research_lab.test_autonomous_research_controller_budget_snapshot", "research_lab.test_autonomous_research_controller_budget_snapshot_validation", "research_lab.test_autonomous_research_controller_budget_snapshot_gate", "research_lab.test_autonomous_research_controller_budget_snapshot_gate_contract", "research_lab.test_autonomous_research_controller_budget_snapshot_gate_bridge", "research_lab.test_autonomous_research_controller_budget_snapshot_gate_bridge_contract", "research_lab.test_autonomous_research_controller_budget_snapshot_gate_bridge_validation", "research_lab.test_autonomous_research_controller_budget_snapshot_gate_bridge_adapter", "research_lab.test_autonomous_research_controller_budget_snapshot_gate_bridge_adapter_contract", "research_lab.test_autonomous_research_controller_budget_snapshot_gate_bridge_adapter_validation", "research_lab.test_autonomous_research_controller_budget_snapshot_gate_bridge_adapter_snapshot", "research_lab.test_autonomous_research_controller_budget_snapshot_gate_bridge_adapter_snapshot_validation", "research_lab.test_autonomous_research_orchestrator_milestone_controller", "research_lab.test_autonomous_research_orchestrator_milestone_state", "research_lab.test_autonomous_research_orchestrator_milestone_state_validation", "research_lab.test_autonomous_research_orchestrator_milestone_supervisor", "research_lab.test_autonomous_research_orchestrator_milestone_supervisor_validation", "research_lab.test_autonomous_research_orchestrator_milestone_report", "research_lab.test_autonomous_research_orchestrator_milestone_report_validation", "research_lab.test_autonomous_research_orchestrator_milestone_notification_adapter", "research_lab.test_autonomous_research_orchestrator_milestone_notification_adapter_validation", "research_lab.test_autonomous_research_orchestrator_milestone_notification_snapshot", "research_lab.test_autonomous_research_orchestrator_milestone_notification_snapshot_validation", "research_lab.test_autonomous_research_orchestrator_milestone_notification_gate", "research_lab.test_autonomous_research_orchestrator_milestone_notification_gate_validation", "research_lab.test_autonomous_research_orchestrator_milestone_notification_contract", "research_lab.test_autonomous_research_orchestrator_milestone_notification_contract_validation", "research_lab.test_autonomous_research_orchestrator_milestone_notification_handoff", "research_lab.test_autonomous_research_orchestrator_milestone_notification_handoff_validation", "research_lab.test_autonomous_research_orchestrator_milestone_notification_envelope", "research_lab.test_autonomous_research_orchestrator_milestone_notification_envelope_validation", "research_lab.test_autonomous_research_orchestrator_milestone_notification_boundary", "research_lab.test_autonomous_research_orchestrator_milestone_notification_boundary_validation", "research_lab.test_autonomous_research_orchestrator_milestone_checkpoint", "research_lab.test_autonomous_research_orchestrator_milestone_checkpoint_validation", "research_lab.test_autonomous_research_orchestrator_milestone_completion_summary", "research_lab.test_autonomous_research_orchestrator_milestone_completion_summary_validation", "research_lab.test_autonomous_research_orchestrator_milestone_v01_completion", "research_lab.test_autonomous_research_orchestrator_milestone_v01_completion_validation", "research_lab.test_autonomous_research_orchestrator_v01_milestone_record", "research_lab.test_autonomous_research_orchestrator_v01_milestone_record_validation", "research_lab.test_autonomous_research_orchestrator_v01_milestone_finalization", "research_lab.test_autonomous_research_orchestrator_v01_milestone_finalization_validation", "research_lab.test_autonomous_research_orchestrator_v01_complete", "research_lab.test_autonomous_research_orchestrator_execution_layer_design", "research_lab.test_autonomous_research_orchestrator_execution_layer_policy", "research_lab.test_autonomous_research_orchestrator_execution_layer_controller", "research_lab.test_autonomous_research_orchestrator_execution_layer_loop", "research_lab.test_autonomous_research_orchestrator_execution_layer_cycle_plan", "research_lab.test_autonomous_research_orchestrator_execution_layer_adapter", "research_lab.test_autonomous_research_orchestrator_execution_layer_adapter_validation",
    ]
    checks = [run_command([sys.executable, "-m", module]) for module in modules]
    passed = all(check["returncode"] == 0 for check in checks)
    snapshot = {"generated_at": datetime.now(timezone.utc).isoformat(),
                "status": "passed" if passed else "failed",
                "stage": "autonomous_research_orchestrator_execution_layer_adapter_validation", "next_theme": "autonomous_research_orchestrator_execution_layer_executor_contract", "checks": checks}
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