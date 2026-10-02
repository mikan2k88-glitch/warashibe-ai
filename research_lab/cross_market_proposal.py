"""Safe cross-market review proposal for PG-014.

A proposal is informational and never authorizes purchase, payment, listing, or
sale. It requires a confirmed domestic comparison and a physically eligible
candidate.
"""

PROPOSAL_VERSION = "0.1"


def build_cross_market_proposal(comparison, candidate):
    if not isinstance(comparison, dict) or not isinstance(candidate, dict):
        raise ValueError("comparison and candidate must be dictionaries")

    if comparison.get("status") != "comparison_ready" or comparison.get("same_identity") is not True:
        return {
            "status": "blocked",
            "reason": "comparison_not_ready",
            "commerce_authorized": False,
            "external_action_authorized": False,
        }

    physical = (candidate.get("evaluation") or {}).get("physical") or {}
    policy = physical.get("policy") or {}
    if policy.get("allowed") is not True:
        return {
            "status": "blocked",
            "reason": "physical_policy_not_allowed",
            "commerce_authorized": False,
            "external_action_authorized": False,
        }

    source = candidate.get("source")
    sources = comparison.get("sources") or ()
    if source not in sources:
        return {
            "status": "blocked",
            "reason": "candidate_source_not_in_comparison",
            "commerce_authorized": False,
            "external_action_authorized": False,
        }

    return {
        "version": PROPOSAL_VERSION,
        "status": "proposal_ready",
        "proposal_type": "review_candidate",
        "candidate_name": candidate.get("name"),
        "candidate_source": source,
        "candidate_purchase_price_jpy": candidate.get("purchase_price"),
        "reference_lowest_asking_price_jpy": comparison.get("lowest_asking_price_jpy"),
        "reference_lowest_asking_source": comparison.get("lowest_asking_source"),
        "reference_price_spread_jpy": comparison.get("price_spread_jpy"),
        "identity_type": comparison.get("identity_type"),
        "identity_value": comparison.get("identity_value"),
        "physical_fit": policy.get("physical_fit"),
        "human_review_required": True,
        "commerce_authorized": False,
        "external_action_authorized": False,
        "purchase_authorized": False,
        "payment_authorized": False,
        "sale_authorized": False,
    }
