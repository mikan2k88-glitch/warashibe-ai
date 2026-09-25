"""Deterministic dry-run pipeline for Warashibe AI real-world mode.

The pipeline uses local fixtures only and stops at the HUMAN GATE boundary.
It performs no network calls and no external or commercial actions.
"""

from real_world_engine import select_real_world_candidate

REAL_WORLD_DRY_RUN_PIPELINE_VERSION = "0.1"

DEFAULT_FIXTURES = (
    {
        "name": "used-game-fast",
        "item_id": "fixture-001",
        "provider": "fixture_market",
        "purchase_price_jpy": 2600,
        "estimated_sale_price_jpy": 4300,
        "estimated_fees_jpy": 200,
        "estimated_shipping_jpy": 200,
        "estimated_days_to_sell": 5,
        "liquidation_value_jpy": 2400,
        "market_depth": 0.85,
        "automation_ease": 0.80,
        "confidence": 0.90,
    },
    {
        "name": "specialty-book-slow",
        "item_id": "fixture-002",
        "provider": "fixture_market",
        "purchase_price_jpy": 2500,
        "estimated_sale_price_jpy": 3900,
        "estimated_fees_jpy": 250,
        "estimated_shipping_jpy": 250,
        "estimated_days_to_sell": 18,
        "liquidation_value_jpy": 2100,
        "market_depth": 0.55,
        "automation_ease": 0.75,
        "confidence": 0.78,
    },
    {
        "name": "hobby-risky",
        "item_id": "fixture-003",
        "provider": "fixture_market",
        "purchase_price_jpy": 2600,
        "estimated_sale_price_jpy": 4000,
        "estimated_fees_jpy": 300,
        "estimated_shipping_jpy": 300,
        "estimated_days_to_sell": 20,
        "liquidation_value_jpy": 1400,
        "market_depth": 0.45,
        "automation_ease": 0.55,
        "confidence": 0.65,
    },
)


def run_real_world_dry_run(candidates=None):
    fixtures = tuple(candidates or DEFAULT_FIXTURES)
    selected = select_real_world_candidate(fixtures)

    return {
        "version": REAL_WORLD_DRY_RUN_PIPELINE_VERSION,
        "mode": "real_world_dry_run",
        "input_count": len(fixtures),
        "result": selected,
        "expected_terminal_state": "ready_for_human_gate",
        "reached_human_gate": selected.get("status") == "ready_for_human_gate",
        "network_execution_authorized": False,
        "purchase_authorized": False,
        "listing_authorized": False,
        "payment_authorized": False,
        "refund_authorized": False,
        "ledger_mutation_authorized": False,
        "external_action_authorized": False,
    }
