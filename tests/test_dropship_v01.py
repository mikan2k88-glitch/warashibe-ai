from dropship.economics import evaluate_dropship_economics
from dropship.policy import evaluate_dropship_policy
from dropship.sandbox import run_sandbox_cycle
from dropship.shadow import evaluate_shadow_candidate
from dropship.promotion import assess_promotion
from dropship.runtime import build_runtime_status


def sample_payload():
    return {
        "category": "general",
        "sale_price": 3000,
        "supplier_cost": 1500,
        "supplier_shipping": 300,
        "platform_fee_rate": 0.10,
        "payment_fee_rate": 0.035,
        "ad_cost": 200,
        "expected_return_cost": 100,
        "refund_reserve": 100,
        "other_cost": 0,
        "supplier_allows_dropshipping": True,
        "platform_terms_confirmed": True,
        "supplier_reliable": True,
        "inventory_confirmed": True,
        "delivery_days": 5,
    }


def test_economics_positive_profit():
    result = evaluate_dropship_economics(sample_payload())
    assert result["net_profit"] > 0
    assert result["required_working_capital"] == 1900.0


def test_policy_promotes_complete_low_risk_candidate():
    payload = sample_payload()
    economics = evaluate_dropship_economics(payload)
    result = evaluate_dropship_policy(payload, economics)
    assert result["allowed"] is True
    assert result["status"] == "promotion_ready"
    assert result["live_execution_allowed"] is False


def test_policy_blocks_unconfirmed_supplier_permission():
    payload = sample_payload()
    payload["supplier_allows_dropshipping"] = False
    economics = evaluate_dropship_economics(payload)
    result = evaluate_dropship_policy(payload, economics)
    assert result["allowed"] is False
    assert "supplier_dropshipping_permission_unconfirmed" in result["reasons"]


def test_sandbox_cycle_finishes_without_external_writes():
    result = run_sandbox_cycle(sample_payload())
    assert result["status"] == "completed"
    assert result["state"] == "SETTLED_SANDBOX"
    assert result["external_writes"] is False
    assert result["real_order"] is False


def test_shadow_candidate_can_become_promotion_candidate():
    result = evaluate_shadow_candidate(sample_payload())
    assert result["mode"] == "shadow"
    assert result["evidence_integrity_passed"] is True
    assert result["promotion_candidate"] is True
    assert result["external_writes"] is False


def test_promotion_gate_separates_research_from_live():
    shadow = evaluate_shadow_candidate(sample_payload())
    result = assess_promotion(shadow)
    assert result["promotion_ready"] is True
    assert result["next_stage"] == "sandbox"
    assert result["live_execution_allowed"] is False


def test_runtime_status_remains_non_live():
    result = build_runtime_status()
    assert result["maturity_stage"] == "shadow_sandbox"
    assert result["live_execution_allowed"] is False
    assert result["external_writes_enabled"] is False
