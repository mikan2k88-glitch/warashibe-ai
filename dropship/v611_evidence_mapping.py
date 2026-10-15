"""v6.11: provenance-aware mapping of one observed CJ/eBay candidate.

This adapter never labels inferred/quoted costs as official verified evidence.
"""
from __future__ import annotations
from .v610_single_candidate import evaluate_one

REQUIRED_SOURCE_FIELDS = ("supplier_cost_usd", "supplier_shipping_usd", "sale_total_usd")
MISSING_ACTIONS = {
    "supplier_cost_usd": "obtain_current_cj_product_variant_cost",
    "supplier_shipping_usd": "obtain_cj_freight_for_quantity_one_and_destination",
    "sale_total_usd": "obtain_comparable_ebay_market_quote",
    "platform_fee": "verify_category_seller_fee_tier_and_full_fee_schedule",
    "expected_return_cost": "validate_cj_returns_and_observed_return_loss",
    "refund_reserve": "approve_documented_refund_reserve_model",
    "other_verified_costs_usd": "verify_other_transaction_costs_and_fx",
}

def assess_observed_candidate(observation: dict, *, capital_usd=None) -> dict:
    if not isinstance(observation, dict):
        raise ValueError("observation_must_be_object")
    candidate = {}
    provenance = {}
    for field in REQUIRED_SOURCE_FIELDS:
        record = (observation.get("evidence") or {}).get(field)
        valid = (isinstance(record, dict) and record.get("status") == "known"
                 and record.get("source") in ("cj_api", "ebay_browse_api")
                 and record.get("observed_at") and record.get("currency") == "USD")
        provenance[field] = "verified_observation" if valid else "unknown"
        if valid:
            candidate[field] = record.get("value")
    # No automatic fee, zero-cost, return-rate, or reserve assumptions.
    evaluation = evaluate_one(candidate, capital_usd=capital_usd)
    missing = sorted(set(evaluation["unknown_fields"]) | {
        field for field, state in provenance.items() if state == "unknown"
    })
    return {
        "version": "6.11",
        "candidate_reference": str(observation.get("candidate_id") or "")[:128],
        "source_provenance": provenance,
        "evaluation": evaluation,
        "unknown_fields": missing,
        "next_evidence_actions": sorted(set(
            MISSING_ACTIONS.get(field, "obtain_verifiable_evidence_for_" + field)
            for field in missing
        )),
        "automatic_listing": False,
        "automatic_ordering": False,
        "human_gate_ready": False,
        "live_execution_allowed": False,
    }
