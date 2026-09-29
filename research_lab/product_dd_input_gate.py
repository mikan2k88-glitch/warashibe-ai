"""Offline product due-diligence input gate; missing evidence never becomes a score."""

from math import isfinite

from research_lab.real_world_candidate_scoring_design import score_candidate

REQUIRED_FIELDS = (
    "purchase_price_jpy", "estimated_sale_price_jpy", "estimated_fees_jpy",
    "estimated_shipping_jpy", "estimated_days_to_sell", "liquidation_value_jpy",
    "market_depth", "automation_ease", "confidence",
)
EVIDENCE_FIELDS = ("price_evidence", "sale_evidence", "fee_evidence",
                   "shipping_evidence", "liquidation_evidence")


def evaluate_product_dd(candidate):
    """Gate a fixture on complete numeric inputs and explicit evidence references."""
    if not isinstance(candidate, dict):
        return _hold(("candidate_not_mapping",))
    missing = tuple(field for field in REQUIRED_FIELDS + EVIDENCE_FIELDS
                    if field not in candidate or candidate[field] is None)
    if missing:
        return _hold(tuple("missing_" + field for field in missing))
    invalid = tuple(field for field in EVIDENCE_FIELDS
                    if not isinstance(candidate[field], str) or not candidate[field].strip())
    invalid += tuple(field for field in REQUIRED_FIELDS
                     if isinstance(candidate[field], bool)
                     or not isinstance(candidate[field], (int, float))
                     or not isfinite(candidate[field]))
    if invalid:
        return _hold(tuple("invalid_" + field for field in invalid))
    scoring = score_candidate(candidate)
    if not scoring.get("valid"):
        return _hold(tuple(scoring.get("errors", ("invalid_candidate",))))
    return {
        "status": "eligible_for_offline_comparison" if scoring["eligible"] else "policy_blocked",
        "reasons": scoring["blockers"], "scoring": scoring,
        "one_item_only": True, "scenario_only": True,
        "external_action_authorized": False,
    }


def _hold(reasons):
    return {"status": "hold_missing_or_invalid_evidence", "reasons": reasons,
            "scoring": None, "one_item_only": True, "scenario_only": True,
            "external_action_authorized": False}
