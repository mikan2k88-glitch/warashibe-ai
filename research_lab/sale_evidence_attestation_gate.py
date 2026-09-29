"""Offline review of independently attested sale evidence; no execution grant.

This validates a *claim and its review record*, not the real-world authenticity
of a source. The asking-price-only marker is never cleared by this function.
"""
from datetime import datetime, timedelta
from math import isfinite

from research_lab.sale_evidence_join_gate import review_sale_evidence_join, _dated


def review_attested_sale_evidence(listing, sale, attestation, *, as_of, max_age_days=7):
    base = {
        "status": "hold_sale_attestation", "reasons": (),
        "reviewable_attestation": False, "asking_price_only": True,
        "scenario": None, "external_action_authorized": False,
    }
    pair = review_sale_evidence_join(
        listing, sale, as_of=as_of, max_age_days=max_age_days)
    if not pair["join_reviewable"]:
        return dict(base, reasons=("provenance_pair_not_reviewable",) + tuple(pair["reasons"]))
    if not isinstance(attestation, dict):
        return dict(base, reasons=("missing_attestation",))
    required = ("item_id", "marketplace", "listing_evidence_ref",
                "sale_evidence_ref", "verifier", "verification_method",
                "verification_ref", "verified_at")
    if any(not isinstance(attestation.get(k), str) or not attestation[k].strip()
           for k in required):
        return dict(base, reasons=("incomplete_attestation",))
    if (attestation["item_id"] != listing["item_id"]
            or attestation["marketplace"] != listing["marketplace"]
            or attestation["listing_evidence_ref"] != listing["evidence_ref"]
            or attestation["sale_evidence_ref"] != sale["evidence_ref"]):
        return dict(base, reasons=("attestation_identity_mismatch",))
    if (attestation["verifier"] in (listing["source"], sale["source"])
            or attestation["verification_ref"] in (
                listing["evidence_ref"], sale["evidence_ref"])):
        return dict(base, reasons=("attestation_not_independent",))
    if attestation.get("verification_status") != "verified":
        return dict(base, reasons=("verification_not_confirmed",))
    checked = _dated(attestation["verified_at"])
    now = _dated(as_of)
    if (checked is None or now is None or isinstance(max_age_days, bool)
            or not isinstance(max_age_days, (int, float)) or not isfinite(max_age_days)
            or not 0 < max_age_days <= 36500
            or checked > now or now - checked > timedelta(days=max_age_days)):
        return dict(base, reasons=("invalid_or_stale_verification_time",))
    return dict(base, status="attestation_record_reviewable", reasons=(),
                reviewable_attestation=True)
