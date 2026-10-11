from dropship.economics import evaluate_dropship_economics
from dropship.policy import evaluate_dropship_policy
from dropship.sandbox import run_sandbox_cycle
from dropship.shadow import evaluate_shadow_candidate
from dropship.promotion import assess_promotion
from dropship.runtime import build_runtime_status
from dropship.supplier import evaluate_supplier_offer
from dropship.ranking import rank_supplier_offers
from dropship.commerce import build_sandbox_commerce_plan
from dropship.stop_loss import assess_listing_stop_loss
from dropship.state_machine import transition


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


def test_supplier_offer_evaluation_is_eligible():
    result = evaluate_supplier_offer(sample_payload() | {
        "product_key": "sku-1",
        "name": "sample",
        "supplier": "supplier-a",
        "source": "fixture",
    })
    assert result["eligible"] is True
    assert result["evidence"]["passed"] is True
    assert result["supplier_score"] > 0


def test_supplier_ranking_selects_best_eligible_offer():
    base = sample_payload() | {
        "name": "sample",
        "source": "fixture",
        "supplier": "supplier-a",
    }
    offers = [
        base | {"product_key": "sku-a", "supplier_cost": 1700},
        base | {"product_key": "sku-b", "supplier_cost": 1200, "supplier": "supplier-b"},
        base | {"product_key": "sku-c", "supplier_allows_dropshipping": False},
    ]
    result = rank_supplier_offers(offers)
    assert result["eligible_count"] == 2
    assert result["blocked_count"] == 1
    assert result["best"]["offer"]["product_key"] == "sku-b"
    assert result["live_execution_allowed"] is False


def test_commerce_plan_completes_selected_sandbox_cycle():
    base = sample_payload() | {
        "name": "sample",
        "source": "fixture",
        "supplier": "supplier-a",
    }
    result = build_sandbox_commerce_plan([
        base | {"product_key": "sku-a", "supplier_cost": 1600},
        base | {"product_key": "sku-b", "supplier_cost": 1200, "supplier": "supplier-b"},
    ])
    assert result["status"] == "completed"
    assert result["selected"]["offer"]["product_key"] == "sku-b"
    assert result["supplier_order"]["real_supplier_order"] is False
    assert result["supplier_order"]["automatic_retry_allowed"] is False
    assert result["external_writes"] is False


def test_stop_loss_pauses_bad_listing_without_live_action():
    result = assess_listing_stop_loss({
        "ad_spend": 1200,
        "orders": 0,
        "margin": -0.01,
        "return_rate": 0.2,
        "delay_rate": 0.3,
        "supplier_reliable": False,
        "inventory_confirmed": False,
    })
    assert result["pause_listing"] is True
    assert result["automatic_live_action"] is False


def test_state_machine_rejects_invalid_transition():
    assert transition("DISCOVERED", "SUPPLIER_VERIFIED")["allowed"] is True
    assert transition("DISCOVERED", "SETTLED_SANDBOX")["allowed"] is False
