"""Offline contract for joining listing and independently observed sale evidence.

This is a review gate, not proof that a sale happened, and it grants no execution.
A listing's asking price never becomes a realized sale price or probability.
"""
from datetime import datetime, timedelta
from math import isfinite


def _dated(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
        return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None
    except (TypeError, ValueError, OverflowError):
        return None


def review_sale_evidence_join(listing, sale, *, as_of, max_age_days=7):
    """Validate identity and provenance; return hold unless all checks pass.

    Inputs are mappings with item_id, marketplace, evidence_ref, source,
    observed_at. Sale evidence must independently identify the same item and
    marketplace, and have a distinct source and reference from the listing.
    """
    base = {"status": "hold_evidence_join", "reasons": (), "join_reviewable": False,
            "asking_price_only": True, "scenario": None,
            "external_action_authorized": False}
    if not isinstance(listing, dict) or not isinstance(sale, dict):
        return dict(base, reasons=("invalid_record",))
    if (isinstance(max_age_days, bool) or not isinstance(max_age_days, (int, float))
            or not isfinite(max_age_days) or not 0 < max_age_days <= 36500):
        return dict(base, reasons=("invalid_max_age",))
    now = _dated(as_of)
    if now is None:
        return dict(base, reasons=("invalid_as_of",))
    required = ("item_id", "marketplace", "evidence_ref", "source", "observed_at")
    for name, record in (("listing", listing), ("sale", sale)):
        if any(not isinstance(record.get(key), str) or not record[key].strip()
               for key in required):
            return dict(base, reasons=(name + "_missing_identity_or_provenance",))
    if listing.get("asking_price_only") is not True:
        return dict(base, reasons=("listing_must_remain_asking_price_only",))
    if (listing["item_id"] != sale["item_id"]
            or listing["marketplace"] != sale["marketplace"]):
        return dict(base, reasons=("different_item_or_marketplace",))
    if (listing["source"] == sale["source"]
            or listing["evidence_ref"] == sale["evidence_ref"]):
        return dict(base, reasons=("sale_evidence_not_independent",))
    for name, record in (("listing", listing), ("sale", sale)):
        observed = _dated(record["observed_at"])
        if observed is None or observed > now or now - observed > timedelta(days=max_age_days):
            return dict(base, reasons=(name + "_invalid_or_stale_time",))
    return dict(base, status="reviewable_provenance_pair", reasons=(),
                join_reviewable=True)
