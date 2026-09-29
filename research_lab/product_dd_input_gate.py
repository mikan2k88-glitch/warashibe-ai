"""Offline product due-diligence input gate; missing evidence never becomes a score."""

from math import isfinite
from datetime import datetime, timedelta

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
    metadata = candidate.get("metadata")
    if isinstance(metadata, dict) and metadata.get("asking_price_only") is True:
        return _hold(("asking_price_only",))
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


def evaluate_product_dd_with_provenance(candidate, *, as_of, max_age_days=7):
    """Require a dated source for every fixture reference before scoring."""
    basic = evaluate_product_dd(candidate)
    if basic["status"] != "eligible_for_offline_comparison":
        return basic
    now = _utc_time(as_of)
    if now is None or isinstance(max_age_days, bool) or not isinstance(max_age_days, (int, float)) or not isfinite(max_age_days) or not 0 < max_age_days <= 36500:
        return _hold(("invalid_evidence_clock_or_max_age",))
    metadata = candidate.get("evidence_metadata")
    if not isinstance(metadata, dict):
        return _hold(("missing_evidence_metadata",))
    errors = []
    for field in EVIDENCE_FIELDS:
        record = metadata.get(field)
        if not isinstance(record, dict):
            errors.append("missing_" + field + "_metadata")
            continue
        source = record.get("source")
        observed = _utc_time(record.get("observed_at"))
        if not isinstance(source, str) or not source.strip() or observed is None:
            errors.append("invalid_" + field + "_provenance")
        elif observed > now or now - observed > timedelta(days=max_age_days):
            errors.append("stale_or_future_" + field + "_evidence")
    return _hold(tuple(errors)) if errors else basic


def _utc_time(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None


def _hold(reasons):
    return {"status": "hold_missing_or_invalid_evidence", "reasons": reasons,
            "scoring": None, "one_item_only": True, "scenario_only": True,
            "external_action_authorized": False}
