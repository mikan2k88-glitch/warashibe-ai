from __future__ import annotations

from .evidence import assess_evidence_integrity, normalize_supplier_offer
from .economics import evaluate_dropship_economics
from .policy import evaluate_dropship_policy


def evaluate_supplier_offer(payload: dict) -> dict:
    offer = normalize_supplier_offer(payload)
    evidence = assess_evidence_integrity(offer)
    economics = evaluate_dropship_economics({**payload, **offer})
    policy = evaluate_dropship_policy({**payload, **offer}, economics)

    reliability_score = 0.0
    reliability_score += 0.30 if offer["supplier_allows_dropshipping"] else 0.0
    reliability_score += 0.25 if offer["supplier_reliable"] else 0.0
    reliability_score += 0.20 if offer["inventory_confirmed"] else 0.0
    reliability_score += 0.15 if offer["platform_terms_confirmed"] else 0.0
    reliability_score += 0.10 if 0 < offer["delivery_days"] <= 7 else 0.0

    return {
        "input": dict(payload),
        "offer": offer,
        "evidence": evidence,
        "economics": economics,
        "policy": policy,
        "supplier_score": round(reliability_score, 6),
        "eligible": evidence["passed"] and policy["allowed"],
    }
