from __future__ import annotations

from .economics import evaluate_dropship_economics
from .policy import evaluate_dropship_policy


def evaluate_shadow_candidate(payload: dict) -> dict:
    """Evaluate a candidate with real-like inputs but no listing/order side effects."""
    economics = evaluate_dropship_economics(payload)
    policy = evaluate_dropship_policy(payload, economics)
    evidence = {
        "supplier_permission_confirmed": payload.get("supplier_allows_dropshipping") is True,
        "platform_terms_confirmed": payload.get("platform_terms_confirmed") is True,
        "inventory_confirmed": payload.get("inventory_confirmed") is True,
        "supplier_reliability_confirmed": payload.get("supplier_reliable") is True,
        "sale_price_present": economics.get("sale_price", 0) > 0,
        "supplier_cost_present": economics.get("supplier_cost", 0) > 0,
    }
    evidence_integrity_passed = all(evidence.values())
    promotion_candidate = policy["allowed"] and evidence_integrity_passed
    return {
        "mode": "shadow",
        "status": "promotion_candidate" if promotion_candidate else "collecting",
        "economics": economics,
        "policy": policy,
        "evidence_checks": evidence,
        "evidence_integrity_passed": evidence_integrity_passed,
        "promotion_candidate": promotion_candidate,
        "external_writes": False,
        "real_listing": False,
        "real_order": False,
    }
