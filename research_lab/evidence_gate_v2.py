"""PG-042 evidence-integrity gate built on the PG-039 evidence validator."""
from urllib.parse import urlsplit

from research_lab.evidence_integrity import evaluate_integrity, canonical_source

SAFETY = {
    "human_gate_required": True,
    "external_execution_authorized": False,
    "purchase_authorized": False,
}


def evaluate_evidence_integrity_v2(
    candidate,
    *,
    as_of,
    max_age_days=7,
    min_sold_evidence=2,
    min_independent_domains=2,
):
    base = evaluate_integrity(
        candidate,
        as_of=as_of,
        max_age_days=max_age_days,
        min_sold_evidence=min_sold_evidence,
    )
    reasons = list(base["reasons"])
    evidence = candidate.get("evidence", []) if isinstance(candidate, dict) else []
    accepted = {
        row.get("evidence_id")
        for row in evidence
        if isinstance(row, dict) and row.get("evidence_id") in base["evidence_refs"]
    }
    sold_domains = set()
    canonical_pages = set()
    for row in evidence:
        if not isinstance(row, dict) or row.get("evidence_id") not in accepted:
            continue
        page = canonical_source(row.get("source_url"))
        if page is not None:
            canonical_pages.add(page)
        if row.get("kind") == "sold_price":
            try:
                host = urlsplit(row["source_url"]).hostname
            except (TypeError, ValueError):
                host = None
            if host:
                sold_domains.add(host.lower())
    if (
        isinstance(min_independent_domains, bool)
        or not isinstance(min_independent_domains, int)
        or min_independent_domains < 1
    ):
        reasons.append("invalid_independent_domain_threshold")
    elif len(sold_domains) < min_independent_domains:
        reasons.append("insufficient_independent_sold_domains")
    if len(canonical_pages) != len(accepted):
        reasons.append("canonical_evidence_collision")
    reasons = list(dict.fromkeys(reasons))
    return {
        "pg": "PG-042",
        "status": "pass" if not reasons else "fail",
        "passed": not reasons,
        "reasons": reasons,
        "accepted_evidence_refs": sorted(x for x in accepted if isinstance(x, str)),
        "independent_sold_domains": sorted(sold_domains),
        **SAFETY,
    }
