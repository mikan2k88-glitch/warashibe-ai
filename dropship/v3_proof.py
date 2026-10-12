from __future__ import annotations

from .human_gate import verify_human_approval
from .live_guard import authorize_action
from .market_provider import FixtureMarketProvider
from .provider import FixtureSupplierProvider
from .provider_catalog import list_provider_catalog
from .real_read_readiness import assess_real_read_readiness
from .real_shadow_controller import run_real_shadow_controller
from .research_write_policy import authorize_research_write


def _supplier_offer() -> dict:
    return {
        "product_key": "v3-proof-product",
        "name": "V3 Proof Product",
        "supplier": "proof-supplier",
        "category": "home",
        "supplier_cost": 10,
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


def _history() -> list[dict]:
    rows = []
    for day in range(1, 8):
        for index in range(3):
            rows.append({
                "product_key": "v3-proof-product",
                "sale_price": 20 + index,
                "supplier_cost": 10,
                "inventory_confirmed": True,
                "observed_at": f"2026-10-{day:02d}T00:00:00+00:00",
            })
    return rows


def build_v3_proof() -> dict:
    supplier = FixtureSupplierProvider([_supplier_offer()])
    market = FixtureMarketProvider({
        "V3 Proof Product": [
            {"price": 20, "currency": "USD"},
            {"price": 21, "currency": "USD"},
            {"price": 22, "currency": "USD"},
        ]
    })
    shadow = run_real_shadow_controller(
        supplier,
        market,
        historical_observations=_history(),
        supplier_currency="USD",
        target_currency="USD",
        budget={
            "max_supplier_items": 5,
            "max_market_queries": 5,
            "max_market_quotes_per_query": 10,
        },
        shadow_thresholds={
            "min_observations": 20,
            "min_observation_days": 7,
        },
        mode="fixture_proof",
    )
    real_read = shadow["real_read"]
    readiness = assess_real_read_readiness(
        real_read,
        credential_health={"all_configured": True},
        shadow_days=7,
        shadow_observations=21,
    )
    research_write = authorize_research_write(
        table="dropship_observations",
        operation="insert",
    )
    commerce_write = authorize_research_write(
        table="orders",
        operation="insert",
    )
    live_guard = authorize_action("submit_supplier_order")
    approval = verify_human_approval("8888")
    providers = list_provider_catalog()

    checks = {
        "real_read_completed": real_read["status"] == "completed",
        "real_read_quality_ready": readiness["ready"] is True,
        "shadow_promotion_review_ready": shadow["status"] == "promotion_review_ready",
        "single_ready_product": shadow["ready_product_keys"] == ["v3-proof-product"],
        "research_append_allowed": research_write["allowed"] is True,
        "commerce_table_write_denied": commerce_write["allowed"] is False,
        "live_supplier_order_blocked": live_guard["allowed"] is False,
        "approval_does_not_enable_live": approval["approved"] is True and approval["live_execution_allowed"] is False,
        "provider_catalog_non_live": providers["live_order_provider_enabled"] is False,
        "no_commerce_external_writes": shadow["commerce_external_writes"] is False,
        "automatic_promotion_disabled": shadow["automatic_promotion"] is False,
    }

    return {
        "proof_version": "3.0",
        "passed": all(checks.values()),
        "checks": checks,
        "shadow": shadow,
        "real_read_readiness": readiness,
        "provider_catalog": providers,
        "live_execution_allowed": False,
    }


def build_v3_acceptance() -> dict:
    proof = build_v3_proof()
    checks = {
        "proof_passed": proof["passed"],
        "promotion_review_reached": proof["shadow"]["status"] == "promotion_review_ready",
        "human_review_required": all(
            row["human_gate_required"] is True
            for row in proof["shadow"]["promotion_reviews"]
            if row["eligible_for_human_review"]
        ),
        "automatic_promotion_disabled": proof["shadow"]["automatic_promotion"] is False,
        "live_execution_disabled": proof["live_execution_allowed"] is False,
    }
    return {
        "acceptance_version": "3.0",
        "passed": all(checks.values()),
        "checks": checks,
        "maturity_ceiling": "promotion_review_human_gate",
        "next_phase": "real_provider_shadow_evidence",
        "live_execution_allowed": False,
    }
