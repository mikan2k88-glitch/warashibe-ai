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
from dropship.hq import build_hq_status
from dropship.human_gate import prepare_human_gate_package, verify_human_approval
from dropship.repository import MemoryAppendOnlyRepository
from dropship.freshness import assess_freshness
from dropship.provider_registry import ProviderRegistry, ProviderDescriptor
from dropship.runtime_controller import run_runtime_controller
from dropship.dll_resilience import RegistryCache
from dropship.dependency_health import build_dependency_health
from dropship.strategy_experiment import compare_strategies
from dropship.walk_forward import run_walk_forward
from dropship.strategy_promotion import assess_strategy_promotion
from dropship.preflight import run_preflight
from dropship.platform_adapter import SandboxSalesChannelAdapter
from dropship.outcome import build_outcome_record
from dropship.learning import summarize_learning, propose_learning_actions
from dropship.campaign import run_sandbox_campaign
from dropship.research_plan import build_next_research_plan
from dropship.orchestrator import run_orchestrator
from dropship.v2_proof import build_v2_proof, build_v2_acceptance
from dropship.manifest import build_manifest
from dropship.provider_config import ProviderConfig
from dropship.provider_normalizer import normalize_provider_row
from dropship.dedupe import deduplicate_observations
from dropship.shadow_collector import collect_shadow_observations
from dropship.auth import describe_auth_config
from dropship.pagination import extract_items, next_page_url
from dropship.daily_summary import build_daily_shadow_summary
from dropship.observation_record import build_observation_record
from dropship.field_mapping import apply_field_mapping, validate_field_mapping
from dropship.data_quality import assess_data_quality, filter_quality
from dropship.candidate_builder import build_latest_candidates
from dropship.collection_pipeline import run_collection_pipeline
from dropship.market_price import summarize_market_quotes
from dropship.pricing_enrichment import enrich_candidate_with_market_price
from dropship.cj_provider import normalize_cj_product
from dropship.printful_provider import normalize_printful_product
from dropship.provider_catalog import list_provider_catalog
from dropship.market_match import build_market_query
from dropship.opportunity import evaluate_opportunity
from dropship.opportunity_pipeline import rank_opportunities
from dropship.ebay_market_provider import normalize_ebay_item
from dropship.credential_health import check_credential_env
from dropship.source_budget import normalize_source_budget
from dropship.research_write_policy import authorize_research_write
from dropship.real_read_runner import run_real_read_research
from dropship.market_provider import FixtureMarketProvider
from dropship.shadow_metrics import build_shadow_metrics
from dropship.shadow_gate import assess_shadow_gate
from dropship.evidence_pack import build_real_read_evidence_pack
from dropship.run_repository import MemoryResearchRunRepository
from dropship.evidence_service import record_evidence_pack
from dropship.real_shadow_controller import run_real_shadow_controller
from dropship.run_quality import assess_run_quality
from dropship.provider_failover import fetch_first_available, search_first_available_market
from dropship.circuit_breaker import ReadOnlyCircuitBreaker
from dropship.real_read_readiness import assess_real_read_readiness
from dropship.v3_proof import build_v3_proof, build_v3_acceptance
from dropship.v3_release import build_v3_release_status
from dropship.supabase_rest import SupabaseRestClient
from dropship.supabase_persistence import persist_observations, load_observation_history, persist_run
from dropship.operations_runner import run_persistent_real_shadow
from dropship.persistence_health import assess_persistence_environment
from dropship.ops_status import build_ops_status
from dropship.persistent_ops_status import build_persistent_ops_status
from dropship.deployment_readiness import assess_deployment_readiness
from dropship.startup_preflight import build_startup_preflight


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
        base | {"product_key": "expensive", "supplier_cost": 1300, "supplier_shipping": 300},
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


def test_hq_reports_next_research_bottleneck():
    result = build_hq_status({
        "eligible_count": 2,
        "shadow_days": 5,
        "sandbox_cycles": 0,
        "evidence_integrity_passed": True,
    })
    assert result["current_bottleneck"] == "insufficient_shadow_days"
    assert result["execution_authorized"] is False


def test_human_gate_approval_does_not_enable_live():
    package = prepare_human_gate_package({
        "selected_product_key": "sku-1",
        "expected_net_profit": 200,
        "required_working_capital": 1200,
    })
    verified = verify_human_approval("8888")
    assert package["approval_required"] is True
    assert package["live_execution_allowed"] is False
    assert verified["approved"] is True
    assert verified["live_execution_allowed"] is False


def test_memory_repository_is_append_only_contract():
    repo = MemoryAppendOnlyRepository()
    repo.append_observation({"product_key": "sku-1"})
    repo.append_observation({"product_key": "sku-1"})
    assert len(repo.observations) == 2


def test_freshness_gate_rejects_stale_observation():
    result = assess_freshness(
        "2026-10-01T00:00:00+00:00",
        now="2026-10-03T00:00:00+00:00",
        max_age_hours=24,
    )
    assert result["fresh"] is False
    assert result["reason"] == "stale_observation"


def test_provider_registry_rejects_order_capable_provider():
    registry = ProviderRegistry()
    registry.register(ProviderDescriptor(name="fixture"))
    assert registry.get("fixture")["mode"] == "read_only"
    try:
        registry.register(ProviderDescriptor(name="unsafe", supports_orders=True))
    except ValueError:
        pass
    else:
        assert False, "order-capable provider must be rejected"


def test_runtime_controller_filters_stale_offers():
    fresh = sample_payload() | {
        "product_key": "fresh",
        "name": "fresh",
        "supplier": "s1",
        "source": "fixture",
        "observed_at": "2026-10-11T04:00:00+00:00",
    }
    stale = sample_payload() | {
        "product_key": "stale",
        "name": "stale",
        "supplier": "s2",
        "source": "fixture",
        "observed_at": "2026-09-01T00:00:00+00:00",
    }
    result = run_runtime_controller([fresh, stale], max_age_hours=48)
    assert result["status"] == "completed"
    assert result["fresh_offer_count"] >= 1
    assert result["stale_offer_count"] >= 1
    assert result["live_execution_allowed"] is False


def test_registry_cache_can_hold_last_good_registry():
    cache = RegistryCache()
    cache.store({"components": [{"id": "x"}]})
    cache.fail(RuntimeError("sleeping"))
    assert cache.registry["components"][0]["id"] == "x"
    assert cache.failures == 1
    assert cache.last_error == "sleeping"


def test_dependency_health_allows_research_when_dll_degraded():
    result = build_dependency_health(dll_status="unavailable", provider_count=1)
    assert result["status"] == "degraded"
    assert result["research_can_continue_without_dll_live"] is True
    assert result["live_execution_allowed"] is False


def _strategy_batch(cost):
    return [sample_payload() | {
        "product_key": f"sku-{cost}",
        "name": "sample",
        "source": "fixture",
        "supplier": "supplier-a",
        "supplier_cost": cost,
    }]


def test_strategy_experiment_compares_without_tuning():
    result = compare_strategies(
        [_strategy_batch(900), _strategy_batch(1000), _strategy_batch(1100)],
        available_capital=3000,
    )
    assert result["recommended_strategy"] in {"safe", "balanced", "aggressive"}
    assert len(result["strategies"]) == 3
    assert result["parameter_tuning_performed"] is False
    assert result["live_execution_allowed"] is False


def test_walk_forward_requires_multiple_windows():
    windows = [
        {"label": "w1", "test_batches": [_strategy_batch(900)]},
        {"label": "w2", "test_batches": [_strategy_batch(1000)]},
        {"label": "w3", "test_batches": [_strategy_batch(1100)]},
    ]
    result = run_walk_forward(
        windows,
        strategy="balanced",
        available_capital=3000,
        min_windows=3,
    )
    assert result["window_count"] == 3
    assert result["research_usable"] is True
    assert result["parameter_tuning_performed"] is False
    assert result["live_execution_allowed"] is False


def test_strategy_promotion_never_auto_changes():
    result = assess_strategy_promotion(
        {"completion_rate": 0.8, "average_expected_net_profit": 100},
        {"completion_rate": 0.8, "average_expected_net_profit": 120},
    )
    assert result["promote_challenger"] is True
    assert result["human_review_required"] is True
    assert result["automatic_strategy_change"] is False


def test_sandbox_sales_channel_is_preview_only():
    preview = SandboxSalesChannelAdapter().build_listing_preview({
        "product_key": "sku-preview",
        "name": "Preview Product",
        "sale_price": 2500,
    })
    assert preview["status"] == "preview_only"
    assert preview["external_write"] is False
    assert preview["live_listing_created"] is False


def test_preflight_passes_safe_fresh_candidate():
    candidate = sample_payload() | {
        "product_key": "sku-preflight",
        "name": "sample",
        "supplier": "supplier-a",
        "source": "fixture",
        "observed_at": "2026-10-11T04:00:00+00:00",
    }
    result = run_preflight(candidate, available_capital=3000, max_age_hours=48)
    assert result["passed"] is True
    assert result["listing_preview"]["external_write"] is False
    assert result["live_execution_allowed"] is False


def test_policy_profile_can_block_slow_delivery():
    candidate = sample_payload() | {"delivery_days": 20}
    result = run_preflight(
        candidate,
        available_capital=3000,
        max_age_hours=99999,
        policy_profile={"max_delivery_days": 10},
    )
    assert result["passed"] is False
    assert "delivery_days_exceed_profile" in result["policy"]["reasons"]


def test_outcome_learning_loop_remains_research_only():
    outcomes = [
        build_outcome_record({"product_key": "a", "supplier": "s1", "category": "general", "strategy": "balanced", "expected_net_profit": 100, "realized_net_profit": 120, "delivered": True}),
        build_outcome_record({"product_key": "b", "supplier": "s1", "category": "general", "strategy": "balanced", "expected_net_profit": 100, "realized_net_profit": 80, "delivered": True}),
        build_outcome_record({"product_key": "c", "supplier": "s2", "category": "general", "strategy": "safe", "expected_net_profit": 50, "realized_net_profit": 60, "delivered": True}),
    ]
    summary = summarize_learning(outcomes)
    actions = propose_learning_actions(summary)
    assert summary["outcome_count"] == 3
    assert summary["automatic_strategy_change"] is False
    assert actions["automatic_execution"] is False


def test_sandbox_campaign_uses_zero_real_orders():
    base = sample_payload() | {
        "product_key": "campaign",
        "name": "sample",
        "source": "fixture",
        "supplier": "supplier-a",
    }
    result = run_sandbox_campaign([[base], [base]], strategy="balanced", available_capital=3000)
    assert result["cycles"] == 2
    assert result["real_orders"] == 0
    assert result["external_writes"] is False
    assert result["live_execution_allowed"] is False


def test_research_plan_prioritizes_evidence_gap():
    result = build_next_research_plan({
        "eligible_candidates": 5,
        "shadow_days": 30,
        "walk_forward_windows": 3,
        "sandbox_cycles": 10,
        "evidence_integrity_passed": False,
    })
    assert result["next_task"] == "repair_evidence_integrity"
    assert result["execution_authorized"] is False


def test_v2_orchestrator_full_research_loop():
    base = sample_payload() | {
        "name": "sample",
        "source": "fixture",
        "supplier": "supplier-a",
        "observed_at": "2026-10-11T04:00:00+00:00",
    }
    batches = [
        [base | {"product_key": "v2-a", "supplier_cost": 1200}],
        [base | {"product_key": "v2-b", "supplier_cost": 1100}],
        [base | {"product_key": "v2-c", "supplier_cost": 1000}],
    ]
    result = run_orchestrator(
        batches,
        available_capital=3000,
        strategy="balanced",
        state={
            "shadow_observations": 20,
            "shadow_days": 30,
            "sandbox_cycles": 10,
            "walk_forward_windows": 3,
            "evidence_integrity_passed": True,
            "ready_for_human_gate": True,
        },
    )
    assert result["status"] == "orchestration_complete"
    assert result["controller"]["status"] == "completed"
    assert result["snapshot"]["append_only_intent"] is True
    assert result["external_writes"] is False
    assert result["live_execution_allowed"] is False


def test_v2_proof_and_acceptance_pass():
    proof = build_v2_proof()
    acceptance = build_v2_acceptance()
    assert proof["passed"] is True
    assert acceptance["passed"] is True
    assert proof["live_execution_allowed"] is False
    assert acceptance["live_execution_allowed"] is False


def test_flask_v20_endpoints_smoke():
    from app import app
    client = app.test_client()
    proof = client.get("/dropship/v2.0/proof")
    acceptance = client.get("/dropship/v2.0/acceptance")
    assert proof.status_code == 200
    assert acceptance.status_code == 200
    assert proof.get_json()["passed"] is True
    assert acceptance.get_json()["passed"] is True


def test_manifest_and_health_are_non_live():
    manifest = build_manifest()
    assert manifest["version"] == "3.0"
    assert manifest["endpoint_count"] >= 20
    assert manifest["live_execution_allowed"] is False

    from app import app
    client = app.test_client()
    health = client.get("/dropship/health")
    manifest_response = client.get("/dropship/v2.0/manifest")
    assert health.status_code == 200
    assert health.get_json()["status"] == "ok"
    assert health.get_json()["live_execution_allowed"] is False
    assert manifest_response.status_code == 200
    assert manifest_response.get_json()["live_execution_allowed"] is False


def test_provider_config_forbids_write_mode():
    result = ProviderConfig(name="x", url="https://example.com", mode="write").validate()
    assert result["valid"] is False
    assert "provider_must_be_read_only" in result["reasons"]


def test_provider_normalizer_maps_common_aliases():
    row = normalize_provider_row(
        {"sku": "s1", "title": "T", "price": 2000, "cost": 1000, "in_stock": True},
        provider_name="demo",
    )
    assert row["product_key"] == "s1"
    assert row["name"] == "T"
    assert row["sale_price"] == 2000
    assert row["supplier_cost"] == 1000
    assert row["source"] == "demo"


def test_dedupe_removes_duplicate_observations():
    rows = [
        {"product_key": "a", "supplier": "s", "source": "x", "sale_price": 1000, "supplier_cost": 500},
        {"product_key": "a", "supplier": "s", "source": "x", "sale_price": 1000, "supplier_cost": 500},
    ]
    result = deduplicate_observations(rows)
    assert result["unique_count"] == 1
    assert result["duplicate_count"] == 1


def test_shadow_collector_is_read_only_and_persistable():
    provider = FixtureSupplierProvider([
        {"product_key": "a", "name": "A", "sale_price": 2000, "supplier_cost": 1000},
        {"product_key": "a", "name": "A", "sale_price": 2000, "supplier_cost": 1000},
    ])
    repo = MemoryAppendOnlyRepository()
    result = collect_shadow_observations(provider, repository=repo)
    assert result["status"] == "completed"
    assert result["duplicate_count"] == 1
    assert result["persisted"] == 1
    assert len(repo.observations) == 1
    assert result["external_writes"] is False
    assert result["live_execution_allowed"] is False


def test_auth_description_never_exposes_secret():
    result = describe_auth_config(token_env="TOKEN", api_key_env="KEY")
    assert result["secrets_exposed"] is False
    assert result["mode"] == "read_only"


def test_generic_pagination_extracts_items_and_next():
    payload = {"items": [{"id": 1}], "next": "https://example.com/page/2"}
    assert extract_items(payload) == [{"id": 1}]
    assert next_page_url(payload) == "https://example.com/page/2"


def test_observation_record_adds_fingerprint():
    result = build_observation_record({
        "product_key": "sku-x",
        "supplier": "s1",
        "source": "fixture",
        "sale_price": 2000,
        "supplier_cost": 1000,
    })
    assert result["product_key"] == "sku-x"
    assert len(result["observation_fingerprint"]) == 64


def test_daily_shadow_summary_aggregates_days():
    result = build_daily_shadow_summary([
        {"product_key": "a", "sale_price": 2000, "supplier_cost": 1000, "inventory_confirmed": True, "observed_at": "2026-10-10T00:00:00+00:00"},
        {"product_key": "b", "sale_price": 3000, "supplier_cost": 1500, "inventory_confirmed": False, "observed_at": "2026-10-10T01:00:00+00:00"},
        {"product_key": "a", "sale_price": 2200, "supplier_cost": 1100, "inventory_confirmed": True, "observed_at": "2026-10-11T00:00:00+00:00"},
    ])
    assert result["day_count"] == 2
    assert result["days"][0]["observations"] == 2
    assert result["live_execution_allowed"] is False


def test_field_mapping_supports_nested_provider_shape():
    mapping = {
        "product_key": "variant.sku",
        "name": "product.title",
        "sale_price": "pricing.retail",
        "supplier_cost": "pricing.cost",
    }
    assert validate_field_mapping(mapping)["valid"] is True
    result = apply_field_mapping({
        "variant": {"sku": "sku-nested"},
        "product": {"title": "Nested Product"},
        "pricing": {"retail": 3000, "cost": 1200},
    }, mapping)
    assert result["product_key"] == "sku-nested"
    assert result["name"] == "Nested Product"
    assert result["sale_price"] == 3000
    assert result["supplier_cost"] == 1200


def test_data_quality_blocks_missing_supplier():
    row = {
        "product_key": "x",
        "name": "X",
        "sale_price": 2000,
        "supplier_cost": 1000,
        "delivery_days": 5,
        "inventory_confirmed": True,
        "source": "fixture",
        "observed_at": "2026-10-11T00:00:00+00:00",
    }
    quality = assess_data_quality(row)
    assert quality["critical_fields_passed"] is False
    assert quality["promotion_data_ready"] is False


def test_candidate_builder_uses_latest_observation():
    rows = [
        {"product_key": "a", "sale_price": 1000, "observed_at": "2026-10-10T00:00:00+00:00"},
        {"product_key": "a", "sale_price": 1200, "observed_at": "2026-10-11T00:00:00+00:00"},
    ]
    result = build_latest_candidates(rows)
    assert len(result) == 1
    assert result[0]["sale_price"] == 1200
    assert result[0]["observation_count"] == 2


def test_collection_pipeline_builds_candidates_and_stays_non_live():
    rows = [
        {
            "product_key": "sku-p",
            "name": "Product",
            "supplier": "supplier-a",
            "category": "general",
            "sale_price": 3000,
            "supplier_cost": 1200,
            "supplier_shipping": 200,
            "delivery_days": 5,
            "inventory_confirmed": True,
            "supplier_allows_dropshipping": True,
            "platform_terms_confirmed": True,
            "supplier_reliable": True,
            "observed_at": "2026-10-11T04:00:00+00:00",
        }
    ]
    result = run_collection_pipeline(
        rows,
        provider_name="fixture",
        max_age_hours=48,
        min_quality_score=0.8,
    )
    assert result["status"] == "completed"
    assert result["candidate_count"] == 1
    assert result["runtime"]["live_execution_allowed"] is False
    assert result["external_writes"] is False


def test_market_quote_summary_uses_median():
    result = summarize_market_quotes([
        {"price": 10, "currency": "USD"},
        {"price": 20, "currency": "USD"},
        {"price": 100, "currency": "USD"},
    ])
    assert result["status"] == "ok"
    assert result["median_price"] == 20.0
    assert result["currency"] == "USD"


def test_pricing_enrichment_joins_supplier_and_market_currency():
    result = enrich_candidate_with_market_price(
        {"product_key": "x", "supplier_cost": 10},
        [
            {"price": 20, "currency": "USD"},
            {"price": 24, "currency": "USD"},
            {"price": 28, "currency": "USD"},
        ],
        supplier_currency="USD",
        target_currency="USD",
        target_discount=0.95,
    )
    assert result["status"] == "ok"
    assert result["candidate"]["sale_price"] == 22.8
    assert result["candidate"]["supplier_cost"] == 10.0
    assert result["live_execution_allowed"] is False


def test_cj_normalizer_stays_research_only():
    result = normalize_cj_product({
        "id": "pid-1",
        "nameEn": "CJ Product",
        "sku": "CJ1",
        "sellPrice": "11.85",
        "totalVerifiedInventory": 5,
        "deliveryCycle": "3-5",
        "threeCategoryName": "Home",
    })
    assert result["product_key"] == "pid-1"
    assert result["supplier_cost"] == 11.85
    assert result["inventory_confirmed"] is True
    assert result["sale_price"] == 0.0
    assert result["supplier_allows_dropshipping"] is False


def test_printful_normalizer_is_discovery_only():
    result = normalize_printful_product({
        "id": 13,
        "title": "T-Shirt",
        "type_name": "T-Shirt",
        "brand": "Brand",
    })
    assert result["supplier"] == "Printful"
    assert result["supplier_cost"] == 0.0
    assert result["metadata"]["provider_stage"] == "catalog_discovery"


def test_provider_catalog_has_no_live_order_provider():
    result = list_provider_catalog()
    assert result["live_order_provider_enabled"] is False
    assert any(row["name"] == "cjdropshipping-list-v2" for row in result["providers"])


def _opportunity_candidate(key, cost):
    return {
        "product_key": key,
        "name": f"Product {key}",
        "supplier": "supplier-a",
        "category": "general",
        "supplier_cost": cost,
        "supplier_shipping": 0,
        "platform_fee_rate": 0.10,
        "payment_fee_rate": 0.035,
        "ad_cost": 0,
        "expected_return_cost": 0,
        "refund_reserve": 0,
        "delivery_days": 5,
        "inventory_confirmed": True,
        "supplier_allows_dropshipping": True,
        "platform_terms_confirmed": True,
        "supplier_reliable": True,
    }


def test_ebay_quote_normalization():
    result = normalize_ebay_item({
        "itemId": "v1|1|0",
        "title": "Comparable",
        "price": {"value": "29.99", "currency": "USD"},
        "condition": "New",
    })
    assert result["price"] == 29.99
    assert result["currency"] == "USD"
    assert result["market"] == "ebay"


def test_market_query_prefers_product_name():
    query = build_market_query({
        "name": "  Sample   Product  ",
        "metadata": {"sku": "ABC"},
    })
    assert query == "Sample Product"


def test_opportunity_requires_market_depth_and_policy():
    candidate = _opportunity_candidate("x", 10)
    quotes = [
        {"price": 20, "currency": "USD"},
        {"price": 21, "currency": "USD"},
        {"price": 22, "currency": "USD"},
    ]
    result = evaluate_opportunity(
        candidate,
        quotes,
        supplier_currency="USD",
        target_currency="USD",
    )
    assert result["status"] == "promotion_candidate"
    assert result["promotion_ready"] is True
    assert result["live_execution_allowed"] is False


def test_opportunity_ranking_selects_better_capital_efficiency():
    candidates = [
        _opportunity_candidate("a", 15),
        _opportunity_candidate("b", 8),
    ]
    quotes = {
        "a": [
            {"price": 25, "currency": "USD"},
            {"price": 26, "currency": "USD"},
            {"price": 27, "currency": "USD"},
        ],
        "b": [
            {"price": 25, "currency": "USD"},
            {"price": 26, "currency": "USD"},
            {"price": 27, "currency": "USD"},
        ],
    }
    result = rank_opportunities(
        candidates,
        quotes,
        supplier_currency="USD",
        target_currency="USD",
    )
    assert result["best"]["product_key"] == "b"
    assert result["evaluated_count"] == 2
    assert result["live_execution_allowed"] is False


def test_source_budget_is_bounded():
    result = normalize_source_budget({
        "max_supplier_items": 9999,
        "max_market_queries": 9999,
        "max_market_quotes_per_query": 9999,
    })
    assert result["max_supplier_items"] == 200
    assert result["max_market_queries"] == 100
    assert result["max_market_quotes_per_query"] == 200


def test_research_write_policy_is_append_only_allowlist():
    allowed = authorize_research_write(
        table="dropship_observations",
        operation="insert",
    )
    denied = authorize_research_write(
        table="orders",
        operation="insert",
    )
    assert allowed["allowed"] is True
    assert allowed["commerce_write"] is False
    assert denied["allowed"] is False


def test_credential_health_never_returns_values(monkeypatch):
    monkeypatch.setenv("TEST_SECRET_A", "super-secret")
    result = check_credential_env(["TEST_SECRET_A", "TEST_SECRET_B"])
    assert result["configured"]["TEST_SECRET_A"] is True
    assert result["configured"]["TEST_SECRET_B"] is False
    assert result["secret_values_exposed"] is False
    assert "super-secret" not in str(result)


def test_real_read_runner_fixture_reaches_opportunity_ranking():
    supplier = FixtureSupplierProvider([
        _opportunity_candidate("runner-1", 10) | {"name": "Runner Product"}
    ])
    market = FixtureMarketProvider({
        "Runner Product": [
            {"price": 20, "currency": "USD"},
            {"price": 21, "currency": "USD"},
            {"price": 22, "currency": "USD"},
        ]
    })
    result = run_real_read_research(
        supplier,
        market,
        supplier_currency="USD",
        target_currency="USD",
        budget={"max_supplier_items": 5, "max_market_queries": 5},
    )
    assert result["status"] == "completed"
    assert result["supplier_candidate_count"] == 1
    assert result["market_query_count"] == 1
    assert result["ranking"]["best"]["product_key"] == "runner-1"
    assert result["commerce_external_writes"] is False
    assert result["live_execution_allowed"] is False


def test_shadow_metrics_and_gate_require_evidence_depth():
    observations = []
    for day in range(1, 8):
        for index in range(3):
            observations.append({
                "product_key": "sku-shadow",
                "sale_price": 20 + index,
                "inventory_confirmed": True,
                "observed_at": f"2026-10-{day:02d}T00:00:00+00:00",
            })
    metrics = build_shadow_metrics(observations)
    product = metrics["products"][0]
    gate = assess_shadow_gate(product)
    assert product["observations"] == 21
    assert product["observation_days"] == 7
    assert gate["passed"] is True
    assert gate["live_execution_allowed"] is False


def test_real_read_evidence_pack_is_append_only_and_non_live():
    run_result = {
        "supplier_provider": "fixture",
        "market_provider": "fixture-market",
        "supplier_candidate_count": 1,
        "market_query_count": 1,
        "market_cache_hits": 0,
        "errors": [],
        "ranking": {
            "best": {
                "product_key": "sku-shadow",
                "opportunity_score": 0.8,
            }
        },
    }
    observations = [
        {
            "product_key": "sku-shadow",
            "sale_price": 20,
            "inventory_confirmed": True,
            "observed_at": "2026-10-01T00:00:00+00:00",
        }
    ]
    pack = build_real_read_evidence_pack(
        run_result,
        observations,
        mode="fixture_proof",
    )
    assert pack["run_record"]["append_only_intent"] is True
    assert len(pack["run_record"]["sha256"]) == 64
    assert pack["live_execution_allowed"] is False


def test_evidence_service_can_append_run_record():
    repo = MemoryResearchRunRepository()
    result = record_evidence_pack(
        {
            "supplier_provider": "fixture",
            "market_provider": "fixture-market",
            "ranking": {"best": {"product_key": "x", "opportunity_score": 0.5}},
        },
        [],
        mode="fixture_proof",
        run_repository=repo,
    )
    assert result["run_record_persisted"] is True
    assert result["research_repository_write"] is True
    assert result["commerce_external_writes"] is False
    assert len(repo.rows) == 1


def test_real_shadow_controller_can_prepare_human_review_without_live():
    supplier_offer = _opportunity_candidate("shadow-ready", 10) | {
        "name": "Shadow Ready Product",
        "observed_at": "2026-10-11T00:00:00+00:00",
    }
    supplier = FixtureSupplierProvider([supplier_offer])
    market = FixtureMarketProvider({
        "Shadow Ready Product": [
            {"price": 20, "currency": "USD"},
            {"price": 21, "currency": "USD"},
            {"price": 22, "currency": "USD"},
        ]
    })
    history = []
    for day in range(1, 8):
        for index in range(3):
            history.append({
                "product_key": "shadow-ready",
                "sale_price": 20 + index,
                "supplier_cost": 10,
                "inventory_confirmed": True,
                "observed_at": f"2026-10-{day:02d}T00:00:00+00:00",
            })

    result = run_real_shadow_controller(
        supplier,
        market,
        historical_observations=history,
        supplier_currency="USD",
        target_currency="USD",
        shadow_thresholds={
            "min_observations": 20,
            "min_observation_days": 7,
        },
        mode="fixture_proof",
    )
    assert result["status"] == "promotion_review_ready"
    assert result["ready_product_keys"] == ["shadow-ready"]
    review = result["promotion_reviews"][0]
    assert review["eligible_for_human_review"] is True
    assert review["automatic_promotion"] is False
    assert review["live_execution_allowed"] is False
    assert result["commerce_external_writes"] is False


class _FailSupplier:
    provider_name = "fail-supplier"
    def fetch_offers(self):
        raise RuntimeError("supplier down")


class _OkSupplier:
    provider_name = "ok-supplier"
    def fetch_offers(self):
        return [{"product_key": "x"}]


class _FailMarket:
    provider_name = "fail-market"
    def search(self, query):
        raise RuntimeError("market down")


class _OkMarket:
    provider_name = "ok-market"
    def search(self, query):
        return [{"price": 10, "currency": "USD"}]


def test_provider_failover_uses_next_available_source():
    supplier = fetch_first_available([_FailSupplier(), _OkSupplier()])
    market = search_first_available_market([_FailMarket(), _OkMarket()], "x")
    assert supplier["status"] == "ok"
    assert supplier["provider_name"] == "ok-supplier"
    assert len(supplier["attempts"]) == 2
    assert market["status"] == "ok"
    assert market["provider_name"] == "ok-market"


def test_read_only_circuit_breaker_opens_after_threshold():
    breaker = ReadOnlyCircuitBreaker(failure_threshold=2)
    assert breaker.allow_request() is True
    breaker.record_failure()
    assert breaker.allow_request() is True
    breaker.record_failure()
    assert breaker.allow_request() is False
    assert breaker.snapshot()["open"] is True
    breaker.record_success()
    assert breaker.allow_request() is True


def test_real_read_readiness_requires_quality_credentials_and_shadow_start():
    run_result = {
        "supplier_candidate_count": 1,
        "market_query_count": 1,
        "errors": [],
        "quotes_by_product": {"x": [{"price": 10, "currency": "USD"}]},
        "ranking": {"evaluated_count": 1},
        "commerce_external_writes": False,
        "live_execution_allowed": False,
    }
    readiness = assess_real_read_readiness(
        run_result,
        credential_health={"all_configured": True},
        shadow_days=1,
        shadow_observations=1,
    )
    assert readiness["ready"] is True
    assert readiness["status"] == "real_read_shadow_ready"
    assert readiness["live_execution_allowed"] is False


def test_v3_proof_reaches_promotion_review_without_live():
    proof = build_v3_proof()
    assert proof["passed"] is True
    assert proof["shadow"]["status"] == "promotion_review_ready"
    assert proof["shadow"]["ready_product_keys"] == ["v3-proof-product"]
    assert proof["live_execution_allowed"] is False


def test_v3_acceptance_and_release_status():
    acceptance = build_v3_acceptance()
    status = build_v3_release_status()
    assert acceptance["passed"] is True
    assert acceptance["maturity_ceiling"] == "promotion_review_human_gate"
    assert status["status"] == "real_read_shadow_endpoint_reached"
    assert status["real_supplier_tokens_required_for_external_read"] is True
    assert status["commerce_external_writes_enabled"] is False
    assert status["live_execution_allowed"] is False


def test_flask_v30_endpoints_smoke():
    from app import app
    client = app.test_client()
    proof = client.get("/dropship/v3.0/proof")
    acceptance = client.get("/dropship/v3.0/acceptance")
    status = client.get("/dropship/v3.0/status")
    assert proof.status_code == 200
    assert acceptance.status_code == 200
    assert status.status_code == 200
    assert proof.get_json()["passed"] is True
    assert acceptance.get_json()["passed"] is True
    assert status.get_json()["status"] == "real_read_shadow_endpoint_reached"


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload
    def raise_for_status(self):
        return None
    def json(self):
        return self._payload


class _FakeSession:
    def __init__(self):
        self.posts = []
        self.gets = []
    def post(self, url, headers, json, timeout):
        self.posts.append({"url": url, "headers": headers, "json": json, "timeout": timeout})
        return _FakeResponse([{"id": 1, **json}])
    def get(self, url, headers, params, timeout):
        self.gets.append({"url": url, "headers": headers, "params": params, "timeout": timeout})
        return _FakeResponse([])


def test_supabase_rest_client_is_server_side_append_only_shape():
    session = _FakeSession()
    client = SupabaseRestClient(
        url="https://example.supabase.co",
        key="server-secret",
        session=session,
    )
    row = client.insert("dropship_research_runs", {"sha256": "x", "mode": "proof"})
    assert row["mode"] == "proof"
    assert session.posts[0]["headers"]["Authorization"] == "Bearer server-secret"
    assert "server-secret" not in str(row)


class _MemoryPersistenceClient:
    def __init__(self):
        self.tables = {
            "dropship_observations": [],
            "dropship_research_runs": [],
        }
    def insert(self, table, row):
        stored = {"id": len(self.tables.setdefault(table, [])) + 1, **dict(row)}
        self.tables[table].append(stored)
        return stored
    def select(self, table, **kwargs):
        return list(self.tables.get(table, []))


def test_persistent_runner_restores_history_and_appends_research_only():
    persistence = _MemoryPersistenceClient()
    supplier = FixtureSupplierProvider([
        _opportunity_candidate("persistent-1", 10) | {"name": "Persistent Product"}
    ])
    market = FixtureMarketProvider({
        "Persistent Product": [
            {"price": 20, "currency": "USD"},
            {"price": 21, "currency": "USD"},
            {"price": 22, "currency": "USD"},
        ]
    })
    first = run_persistent_real_shadow(
        supplier,
        market,
        persistence_client=persistence,
        supplier_currency="USD",
        target_currency="USD",
        shadow_thresholds={"min_observations": 1, "min_observation_days": 1},
        mode="fixture_proof",
    )
    second = run_persistent_real_shadow(
        supplier,
        market,
        persistence_client=persistence,
        supplier_currency="USD",
        target_currency="USD",
        shadow_thresholds={"min_observations": 1, "min_observation_days": 1},
        mode="fixture_proof",
    )
    assert first["research_persistence_enabled"] is True
    assert second["history_loaded"] is True
    assert second["history_count"] >= 1
    assert len(persistence.tables["dropship_observations"]) >= 1
    assert len(persistence.tables["dropship_research_runs"]) == 2
    assert second["commerce_external_writes"] is False
    assert second["live_execution_allowed"] is False


def test_persistence_health_never_exposes_secret(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "hidden")
    result = assess_persistence_environment()
    assert result["status"] == "ready"
    assert result["secret_values_exposed"] is False
    assert "hidden" not in str(result)


def test_ops_status_prioritizes_credentials_before_shadow():
    result = build_ops_status(
        [{"product_key": "x", "observed_at": "2026-10-11T00:00:00+00:00"}],
        [],
        promotion_reviews=[],
    )
    assert result["status"] == "ops_status_ready"
    assert result["next_action"]["automatic_live_action"] is False
    assert result["live_execution_allowed"] is False


def test_persistent_ops_status_reads_database_history():
    persistence = _MemoryPersistenceClient()
    persistence.tables["dropship_observations"].append({
        "product_key": "ops-x",
        "supplier": "s1",
        "source": "fixture",
        "observed_at": "2026-10-11T00:00:00+00:00",
        "observation_fingerprint": "f",
        "observation": {
            "product_key": "ops-x",
            "observed_at": "2026-10-11T00:00:00+00:00",
        },
    })
    persistence.tables["dropship_research_runs"].append({
        "record": {
            "mode": "fixture_proof",
            "observed_at": "2026-10-11T00:01:00+00:00",
        }
    })
    result = build_persistent_ops_status(persistence)
    assert result["database_read_ok"] is True
    assert result["database_observation_count"] == 1
    assert result["database_run_count"] == 1
    assert result["live_execution_allowed"] is False


def test_deployment_readiness_defaults_to_fixture_without_credentials(monkeypatch):
    for name in [
        "CJ_ACCESS_TOKEN",
        "EBAY_ACCESS_TOKEN",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_SECRET_KEY",
    ]:
        monkeypatch.delenv(name, raising=False)
    result = assess_deployment_readiness()
    assert result["mode"] == "fixture_proof"
    assert result["commerce_external_writes_enabled"] is False
    assert result["live_execution_allowed"] is False


def test_deployment_readiness_detects_persistent_real_read(monkeypatch):
    monkeypatch.setenv("CJ_ACCESS_TOKEN", "cj")
    monkeypatch.setenv("EBAY_ACCESS_TOKEN", "ebay")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "secret")
    result = assess_deployment_readiness()
    assert result["mode"] == "real_read_persistent_shadow"
    assert result["live_execution_allowed"] is False


def test_startup_preflight_never_enables_live(monkeypatch):
    monkeypatch.delenv("CJ_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("EBAY_ACCESS_TOKEN", raising=False)
    result = build_startup_preflight()
    assert result["safe_to_start_research_runtime"] is True
    assert result["safe_to_start_live_commerce"] is False
    assert result["live_execution_allowed"] is False
