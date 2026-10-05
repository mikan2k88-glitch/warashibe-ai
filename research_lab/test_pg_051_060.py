from research_lab.strategy_validation import evaluate_walk_forward, evaluate_champion_challenger
from research_lab.runtime_transition import evaluate_runtime_transition
from research_lab.live_pilot import (
    evaluate_limited_live_readiness, build_human_gate_decision_packet, validate_one_item_live_proof,
)
from research_lab.learning_velocity import build_live_outcome_learning, evaluate_capital_velocity
from research_lab.automation_readiness import evaluate_controlled_automation, review_v1_operational_readiness


def test_pg051_walk_forward_passes_stable_windows_without_authority():
    windows = [
        {"return_rate": 0.10, "max_drawdown_rate": 0.10},
        {"return_rate": 0.08, "max_drawdown_rate": 0.12},
        {"return_rate": 0.05, "max_drawdown_rate": 0.09},
    ]
    r = evaluate_walk_forward(windows)
    assert r["walk_forward_passed"] is True
    assert r["purchase_authorized"] is False


def test_pg052_challenger_never_auto_promotes():
    r = evaluate_champion_challenger(
        champion={"strategy_id": "a"}, challenger={"strategy_id": "b"},
        walk_forward_result={"walk_forward_passed": True},
        shadow_result={"shadow_passed": True},
    )
    assert r["promotion_recommended"] is True
    assert r["auto_promote"] is False


def test_pg053_runtime_transition_never_auto_transitions():
    r = evaluate_runtime_transition(
        runtime_status={"runtime_verified": True}, evidence_status={"passed": True},
        recovery_status={"action": "retry_with_backoff"}, current_stage="shadow",
    )
    assert r["transition_recommendation"] == "eligible_for_readiness_review"
    assert r["auto_transition"] is False


def test_pg054_requires_one_item_scope():
    r = evaluate_limited_live_readiness(
        live_readiness={"live_readiness_ready": True},
        burn_in={"burn_in_passed": True}, candidate_count=1,
    )
    assert r["limited_live_review_ready"] is True
    assert r["purchase_authorized"] is False


def test_pg055_human_gate_packet_is_not_purchase_permission():
    r = build_human_gate_decision_packet(
        {"candidate_id": "c1", "product_identity": {}, "source_url": "https://example.com",
         "expected_net_profit": 400, "stop_loss_price": 900, "max_hold_days": 7},
        readiness={"limited_live_review_ready": True},
        evidence_pack={"human_review_ready": True},
        max_loss_jpy=500, decision_deadline="2026-10-07T00:00:00Z",
    )
    assert r["status"] == "human_decision_packet_ready"
    assert r["human_decision_required"] is True
    assert r["purchase_authorized"] is False


def test_pg056_validates_completed_human_supplied_proof_only():
    r = validate_one_item_live_proof({
        "candidate_id": "c1", "purchase_receipt_ref": "p", "inspection_ref": "i",
        "sale_ref": "s", "settlement_ref": "x", "capital_before_jpy": 3000,
        "capital_after_jpy": 3400, "human_approved": True, "max_transactions": 1,
    })
    assert r["proof_valid"] is True
    assert r["capital_delta_jpy"] == 400
    assert r["proof_record_only"] is True


def test_pg057_learning_records_variance_without_auto_strategy_change():
    r = build_live_outcome_learning(
        forecast={"net_profit_jpy": 400, "sale_days": 5, "fees_jpy": 300},
        realized={"net_profit_jpy": 350, "sale_days": 6, "fees_jpy": 330, "failure_factors": []},
    )
    assert r["deltas"]["net_profit_jpy"] == -50
    assert r["auto_strategy_change"] is False


def test_pg058_capital_velocity():
    r = evaluate_capital_velocity(
        capital_before_jpy=3000, capital_after_jpy=3400, cycle_days=4,
    )
    assert r["capital_velocity_jpy_per_day"] == 100
    assert r["purchase_authorized"] is False


def test_pg059_only_safe_scope_can_be_reviewed_for_automation():
    r = evaluate_controlled_automation(
        burn_in={"burn_in_passed": True},
        recovery={"action": "retry_with_backoff"},
        idempotency={"duplicate": False},
        learning={"status": "learning_record_ready"},
        allowed_scope=["market_read", "shadow_observation"],
    )
    assert r["automation_review_ready"] is True
    assert r["commerce_automation_authorized"] is False


def test_pg060_readiness_recommends_operations_mode_not_more_features():
    keys = [
        "ci_green", "runtime_verified", "evidence_integrity", "shadow_operational",
        "promotion_gate", "human_gate", "recovery", "idempotency", "burn_in", "learning_loop",
    ]
    r = review_v1_operational_readiness(checkpoints={k: True for k in keys})
    assert r["v1_operational_readiness"] is True
    assert r["recommended_mode"] == "operations_evidence_collection"
    assert r["new_feature_expansion_recommended"] is False
