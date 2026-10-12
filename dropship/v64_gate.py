from __future__ import annotations

from .cost_completeness import assess_cost_completeness
from .terms_evidence import assess_terms_evidence


def assess_v64_promotion_gate(
    ranked_product: dict,
    promotion_review: dict,
) -> dict:
    candidate = (
        ranked_product.get("candidate")
        or (ranked_product.get("opportunity") or {}).get("candidate")
        or {}
    )
    cost = assess_cost_completeness(candidate)
    terms = assess_terms_evidence(candidate)
    base_ready = promotion_review.get("eligible_for_human_review") is True

    checks = {
        "base_promotion_review_ready": base_ready,
        "cost_complete": cost["passed"],
        "terms_complete": terms["passed"],
    }
    passed = all(checks.values())

    return {
        "gate_version": "6.4",
        "product_key": str(ranked_product.get("product_key") or ""),
        "status": (
            "v64_human_review_ready"
            if passed
            else "v64_evidence_incomplete"
        ),
        "passed": passed,
        "checks": checks,
        "cost_completeness": cost,
        "terms_evidence": terms,
        "eligible_for_human_review": passed,
        "human_gate_required": True,
        "automatic_promotion": False,
        "commerce_write_performed": False,
        "live_execution_allowed": False,
    }
