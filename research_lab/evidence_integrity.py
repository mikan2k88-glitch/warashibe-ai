"""Minimal declared-evidence integrity, not verification of remote source truth."""
from datetime import timedelta
from math import isfinite
from statistics import median
from urllib.parse import urlsplit

from research_lab.product_dd_input_gate import _utc_time

COST_KINDS = {
    "acquisition_price": "acquisition_price", "acquisition_shipping": "acquisition_shipping",
    "acquisition_fees": "acquisition_fees", "selling_fee": "expected_selling_fee",
    "outbound_shipping": "expected_outbound_shipping",
}


def number(value, *, minimum=0):
    return (not isinstance(value, bool) and isinstance(value, (int, float))
            and isfinite(value) and value >= minimum)


def source_url(value):
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        url = urlsplit(value)
        return url.scheme == "https" and bool(url.hostname) and not url.username and not url.password
    except ValueError:
        return False


def identity_valid(identity):
    return (isinstance(identity, dict)
            and all(isinstance(identity.get(k), str) and identity[k].strip()
                    for k in ("product_id", "edition", "condition"))
            and isinstance(identity.get("included_items"), list)
            and all(isinstance(x, str) and x.strip() for x in identity["included_items"])
            and len(set(identity["included_items"])) == len(identity["included_items"])
            and all(k not in identity or identity[k] is None
                    or isinstance(identity[k], str) and bool(identity[k].strip()) for k in ("model", "jan")))


def same_identity(left, right):
    if not identity_valid(left) or not identity_valid(right):
        return False
    return (all(left.get(k) == right.get(k) for k in ("product_id", "edition", "condition", "model", "jan"))
            and sorted(left["included_items"]) == sorted(right["included_items"]))


def evaluate_integrity(candidate, *, as_of, max_age_days=7, min_sold_evidence=2):
    reasons, accepted = [], []
    now = _utc_time(as_of)
    if (now is None or not number(max_age_days, minimum=0.000001) or max_age_days > 36500
            or isinstance(min_sold_evidence, bool) or not isinstance(min_sold_evidence, int)
            or min_sold_evidence < 1):
        return _result(["invalid_evidence_clock_or_threshold"], [])
    if not isinstance(candidate, dict):
        return _result(["candidate_not_mapping"], [])
    identity = candidate.get("product_identity")
    if not identity_valid(identity):
        reasons.append("product_identity_not_confirmed")
    if not source_url(candidate.get("source_url")):
        reasons.append("missing_source_url")
    observed = _utc_time(candidate.get("observed_at"))
    if observed is None or observed > now or now - observed > timedelta(days=max_age_days):
        reasons.append("candidate_stale_or_future")
    evidence = candidate.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        return _result(reasons + ["missing_evidence"], [])
    ids, sources = set(), set()
    for row in evidence:
        if not isinstance(row, dict):
            reasons.append("invalid_evidence_record")
            continue
        errors = []
        key, kind = row.get("evidence_id"), row.get("kind")
        if not isinstance(key, str) or not key.strip() or not isinstance(kind, str) or not kind.strip():
            errors.append("invalid_evidence_id_or_kind")
        if not same_identity(identity, row.get("product_identity")):
            errors.append("product_identity_mismatch")
        if not source_url(row.get("source_url")) or not isinstance(row.get("source"), str) or not row["source"].strip():
            errors.append("invalid_evidence_source")
        timestamp = _utc_time(row.get("observed_at"))
        if timestamp is None or timestamp > now or now - timestamp > timedelta(days=max_age_days):
            errors.append("stale_or_future_evidence")
        # A repeated sold URL cannot be made independent by changing timestamp/id.
        source_key = (kind, row.get("source_url"))
        if isinstance(key, str) and isinstance(kind, str) and isinstance(row.get("source_url"), str):
            if key in ids or source_key in sources:
                errors.append("duplicate_evidence")
            ids.add(key)
            sources.add(source_key)
        if kind in COST_KINDS or kind == "sold_price":
            if not number(row.get("amount")):
                errors.append("invalid_evidence_amount")
        if kind in COST_KINDS:
            expected = candidate.get(COST_KINDS[kind])
            if not number(expected) or row.get("amount") != expected:
                errors.append("cost_evidence_mismatch")
        reasons.extend(errors)
        if not errors:
            accepted.append(row)
    kinds = {row["kind"] for row in accepted}
    for kind in COST_KINDS:
        if kind not in kinds:
            reasons.append("missing_" + kind + "_evidence")
    sold = [row["amount"] for row in accepted if row["kind"] == "sold_price"]
    if len(sold) < min_sold_evidence:
        reasons.append("insufficient_sold_evidence")
    expected_sale = candidate.get("expected_sale_price")
    if not number(expected_sale) or sold and expected_sale > median(sold):
        reasons.append("sale_price_not_supported")
    return _result(reasons, accepted)


def _result(reasons, accepted):
    return {"status": "fail" if reasons else "pass", "passed": not reasons,
            "reasons": list(dict.fromkeys(reasons)),
            "evidence_refs": [row["evidence_id"] for row in accepted],
            "external_execution_authorized": False}
