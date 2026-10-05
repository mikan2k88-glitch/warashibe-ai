from datetime import datetime, timezone

from research_lab.integration_runtime import evaluate_integration_gate, build_runtime_status
from research_lab.live_safety import (
    evaluate_live_readiness, recovery_decision, evaluate_idempotency, evaluate_burn_in,
)
from research_lab.shadow_operations import schedule_shadow_reobservation, compute_shadow_outcome


NOW = "2026-10-06T00:00:00+00:00"
GREEN = [{"status": "completed", "conclusion": "success"}]


def test_pg040_integration_is_fail_closed_and_green_when_evidence_matches():
    result = evaluate_integration_gate(
        expected_head_sha="abc", observed_head_sha="abc", ci_checks=GREEN,
        code_match=True, review_complete=True, draft=False,
    )
    assert result["integration_ready"] is True
    assert result["merge_authorized"] is False
    assert result["purchase_authorized"] is False


def test_pg041_runtime_does_not_infer_unverified_external_state():
    result = build_runtime_status(
        maturity_stage="shadow", head_sha="abc", ci_checks=GREEN,
        render_state="not_verified", supabase_state="not_verified", observed_at=NOW,
    )
    assert result["runtime_verified"] is False
    assert result["external_execution_authorized"] is False


def test_pg043_schedules_read_only_shadow_reobservation():
    row = schedule_shadow_reobservation(
        {"shadow_candidate_id": "shadow-1"}, as_of=NOW, interval_hours=24,
    )
    assert row["status"] == "scheduled"
    assert row["next_observation_at"].startswith("2026-10-07")
    assert row["purchase_authorized"] is False


def test_pg045_shadow_outcome_is_hypothetical_only():
    candidate = {
        "shadow_candidate_id": "shadow-1",
        "total_acquisition_cost": 1000,
        "expected_net_profit": 400,
    }
    observations = [{
        "estimated_sale_price": 1800,
        "expected_selling_fee": 180,
        "expected_outbound_shipping": 210,
        "stock_status": "available",
        "liquidity_score": 0.8,
    }]
    out = compute_shadow_outcome(candidate, observations, as_of=NOW)
    assert out["status"] == "success"
    assert out["hypothetical_net_profit"] == 410
    assert out["hypothetical"] is True
    assert out["external_execution_authorized"] is False


def test_pg047_live_readiness_requires_all_preconditions_but_still_not_authorized():
    result = evaluate_live_readiness(
        integration={"integration_ready": True},
        runtime={"runtime_verified": True},
        evidence={"passed": True},
        shadow_outcomes=[{"status": "success"} for _ in range(3)],
        promotion_pack={"human_review_ready": True},
        kill_switch_ready=True,
        max_loss_jpy=500,
    )
    assert result["live_readiness_ready"] is True
    assert result["requires_explicit_human_go"] is True
    assert result["purchase_authorized"] is False


def test_pg048_commerce_write_never_auto_retries():
    result = recovery_decision(
        operation_class="commerce_write", failure_count=0,
        retryable=True, state_consistent=True,
    )
    assert result["action"] == "stop_and_escalate"
    assert result["fail_closed"] is True


def test_pg049_duplicate_is_blocked():
    result = evaluate_idempotency(
        operation_key="purchase:1",
        seen_operation_keys={"purchase:1": "fp-a"},
        payload_fingerprint="fp-a",
    )
    assert result["duplicate"] is True
    assert result["prepare_only"] is False
    assert result["execute_authorized"] is False


def test_pg050_burn_in_passes_metrics_without_granting_automation():
    rows = [
        {"status": "success", "forecast_variance": 50, "realized_net_profit_jpy": 100}
        for _ in range(5)
    ]
    result = evaluate_burn_in(rows)
    assert result["burn_in_passed"] is True
    assert result["controlled_automation_ready"] is False
    assert result["purchase_authorized"] is False
