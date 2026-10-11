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
from dropship.pipeline import run_dropship_decision_pipeline
from dropship.readiness import assess_live_readiness
from dropship.research_cycle import run_research_cycle
from dropship.observations import summarize_observations
from dropship.live_guard import authorize_action
from dropship.dll_registry import find_components
from dropship.provider import FixtureSupplierProvider
from dropship.duplicate_guard import assess_duplicate_order
from dropship.recovery import classify_recovery
from dropship.audit import create_audit_record
from dropship.burn_in import assess_burn_in
from dropship.evidence_bundle import build_readiness_evidence
from dropship.selection import select_single_candidate
from dropship.maturity import determine_maturity
from dropship.dashboard import build_dashboard_summary
from dropship.controller import run_controller
from dropship.proof import build_proof, build_acceptance
from dropship.snapshot import build_research_snapshot
from dropship.release import build_release_status


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


def test_decision_pipeline_reaches_sandbox_settlement():
    base = sample_payload() | {
        "name": "sample",
        "source": "fixture",
        "supplier": "supplier-a",
    }
    result = run_dropship_decision_pipeline([
        base | {"product_key": "sku-a", "supplier_cost": 1600},
        base | {"product_key": "sku-b", "supplier_cost": 1200, "supplier": "supplier-b"},
    ])
    assert result["status"] == "completed"
    assert result["stage"] == "sandbox_settlement"
    assert result["selected_product_key"] == "sku-b"
    assert result["external_writes"] is False
    assert result["live_execution_allowed"] is False


def test_live_readiness_only_reaches_human_gate():
    result = assess_live_readiness({
        "shadow_observations": 20,
        "shadow_days": 30,
        "sandbox_cycles": 10,
        "evidence_integrity_passed": True,
        "promotion_gate_passed": True,
        "duplicate_order_guard": True,
        "kill_switch_ready": True,
        "audit_log_ready": True,
        "external_writes_enabled": False,
    })
    assert result["status"] == "ready_for_human_gate"
    assert result["research_ready_for_human_gate"] is True
    assert result["live_execution_allowed"] is False
    assert result["human_gate_required"] is True


def test_fixture_provider_is_read_only_shape():
    provider = FixtureSupplierProvider([
        {"product_key": "sku-x", "name": "x", "sale_price": 1000}
    ])
    rows = provider.fetch_offers()
    assert len(rows) == 1
    assert rows[0]["source"] == "fixture"
    assert "observed_at" in rows[0]


def test_observation_summary_groups_product_history():
    rows = [
        {"product_key": "sku-x", "sale_price": 1000, "supplier_cost": 500, "delivery_days": 4, "inventory_confirmed": True, "observed_at": "2026-10-01T00:00:00+00:00"},
        {"product_key": "sku-x", "sale_price": 1100, "supplier_cost": 550, "delivery_days": 5, "inventory_confirmed": True, "observed_at": "2026-10-02T00:00:00+00:00"},
    ]
    result = summarize_observations(rows)
    assert result["total_observations"] == 2
    assert result["product_count"] == 1
    assert result["products"][0]["observation_days"] == 2


def test_research_cycle_remains_non_live():
    base = sample_payload() | {
        "product_key": "sku-r",
        "name": "sample",
        "source": "fixture",
        "supplier": "supplier-a",
    }
    result = run_research_cycle([base])
    assert result["status"] == "completed"
    assert result["mode"] == "research"
    assert result["external_writes"] is False
    assert result["live_execution_allowed"] is False


def test_live_guard_default_deny_for_live_actions():
    assert authorize_action("fetch_inventory")["allowed"] is True
    blocked = authorize_action("submit_supplier_order", human_approved=True)
    assert blocked["allowed"] is False
    assert blocked["human_approval_required"] is True


def test_dll_registry_keyword_matcher():
    registry = {"components": [{"id": "retry", "name": "HTTP Retry Client"}, {"id": "db", "name": "Database"}]}
    matches = find_components(registry, ["retry", "http"])
    assert matches
    assert matches[0]["component"]["id"] == "retry"


def test_duplicate_order_guard_is_deterministic():
    order = {"customer_order_id": "c1", "product_key": "sku-1", "supplier": "s1", "quantity": 1}
    first = assess_duplicate_order(order, [])
    second = assess_duplicate_order(order, [first["fingerprint"]])
    assert first["allowed"] is True
    assert second["duplicate"] is True
    assert second["allowed"] is False


def test_recovery_allows_only_transient_reads():
    retry = classify_recovery("fetch_inventory", "timeout", attempts=0)
    assert retry["retry_allowed"] is True
    blocked = classify_recovery("submit_supplier_order", "timeout", attempts=0)
    assert blocked["retry_allowed"] is False
    assert blocked["classification"] == "hard_block"


def test_audit_record_has_digest():
    record = create_audit_record("candidate_evaluated", {"product_key": "sku-1"})
    assert record["append_only_intent"] is True
    assert len(record["sha256"]) == 64


def test_burn_in_does_not_enable_controlled_automation():
    result = assess_burn_in({
        "cycles": 20,
        "failure_rate": 0.01,
        "duplicate_orders": 0,
        "policy_violations": 0,
        "unhandled_errors": 0,
        "median_net_profit": 100,
    })
    assert result["passed"] is True
    assert result["controlled_automation_allowed"] is False


def test_readiness_evidence_stops_at_human_gate():
    result = build_readiness_evidence(
        shadow_observations=20,
        shadow_days=30,
        sandbox_cycles=10,
        evidence_integrity_passed=True,
        promotion_gate_passed=True,
    )
    assert result["readiness"]["status"] == "ready_for_human_gate"
    assert result["live_execution_allowed"] is False


def test_single_selection_obeys_capital_and_one_item_rule():
    base = sample_payload() | {
        "name": "sample",
        "source": "fixture",
        "supplier": "supplier-a",
    }
    ranking = rank_supplier_offers([
        base | {"product_key": "cheap", "supplier_cost": 800, "supplier_shipping": 100},
        base | {"product_key": "expensive", "supplier_cost": 2500, "supplier_shipping": 500},
    ])
    result = select_single_candidate(ranking, strategy="balanced", available_capital=1500)
    assert result["one_item_only"] is True
    assert result["selected"]["offer"]["product_key"] == "cheap"
    assert result["capital_blocked_count"] == 1


def test_maturity_never_enables_live_by_itself():
    result = determine_maturity({
        "shadow_observations": 30,
        "sandbox_cycles": 20,
        "ready_for_human_gate": True,
    })
    assert result["stage"] == "live_readiness"
    assert result["allowed_actions"]["live_listing"] is False
    assert result["allowed_actions"]["live_supplier_order"] is False


def test_dashboard_summary_stays_non_live():
    result = build_dashboard_summary({
        "version": "0.8",
        "candidate_count": 10,
        "eligible_count": 3,
        "shadow_observations": 30,
        "shadow_days": 30,
        "sandbox_cycles": 10,
        "ready_for_human_gate": True,
        "estimated_net_profit": 250,
    })
    assert result["maturity"]["stage"] == "live_readiness"
    assert result["live_execution_allowed"] is False
    assert result["next_focus"] == "human_gate_review"


def test_controller_respects_strategy_and_capital():
    base = sample_payload() | {
        "name": "sample",
        "source": "fixture",
        "supplier": "supplier-a",
    }
    result = run_controller([
        base | {"product_key": "a", "supplier_cost": 2400, "supplier_shipping": 400},
        base | {"product_key": "b", "supplier_cost": 900, "supplier_shipping": 100, "supplier": "supplier-b"},
    ], strategy="balanced", available_capital=1500)
    assert result["status"] == "completed"
    assert result["selected_product_key"] == "b"
    assert result["required_working_capital"] <= 1500
    assert result["live_execution_allowed"] is False


def test_v09_proof_passes_without_live_writes():
    result = build_proof()
    assert result["passed"] is True
    assert result["controller"]["live_execution_allowed"] is False
    assert result["guards"]["live_write_blocked"]["allowed"] is False


def test_v09_acceptance_stops_at_human_gate():
    result = build_acceptance()
    assert result["passed"] is True
    assert result["readiness"]["status"] == "ready_for_human_gate"
    assert result["live_execution_allowed"] is False


def test_research_snapshot_is_append_only_and_non_live():
    result = build_research_snapshot({
        "maturity_stage": "sandbox",
        "candidate_count": 8,
        "eligible_count": 2,
        "shadow_observations": 20,
        "shadow_days": 10,
        "sandbox_cycles": 5,
        "selected_product_key": "sku-1",
        "estimated_net_profit": 300,
    })
    assert result["append_only_intent"] is True
    assert result["external_writes"] is False
    assert result["live_execution_allowed"] is False
    assert len(result["sha256"]) == 64


def test_v10_release_status_reaches_research_endpoint():
    result = build_release_status()
    assert result["status"] == "research_endpoint_reached"
    assert result["capabilities"]["live_commerce_enabled"] is False
    assert result["maturity_ceiling"] == "ready_for_human_gate"
    assert result["live_execution_allowed"] is False


def test_flask_v10_proof_and_status_smoke():
    from app import app
    client = app.test_client()
    proof = client.get("/dropship/v1.0/proof")
    status = client.get("/dropship/v1.0/status")
    assert proof.status_code == 200
    assert proof.get_json()["passed"] is True
    assert status.status_code == 200
    assert status.get_json()["status"] == "research_endpoint_reached"
