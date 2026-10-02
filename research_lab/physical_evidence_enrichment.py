"""Deterministic physical-evidence enrichment for PG-014.

Only explicit, provenance-bearing evidence may fill physical fields. Identity
must match the candidate's canonical GTIN. No network calls or commerce actions
are performed.
"""

from copy import deepcopy

from research_lab.initial_physical_operation_policy import evaluate_initial_physical_fit
from research_lab.identifier_validation import is_valid_gtin, normalize_gtin

ENRICHMENT_VERSION = "0.1"
ALLOWED_SOURCE_KINDS = {
    "manufacturer_spec",
    "official_product_page",
    "marketplace_shipping_spec",
}
PHYSICAL_FIELDS = (
    "package_size_class",
    "weight_grams",
    "shipping_cost_jpy",
    "fragility_score",
    "storage_score",
    "domestic_shipping",
)


def enrich_candidate_with_physical_evidence(candidate, evidence):
    if not isinstance(candidate, dict) or not isinstance(evidence, dict):
        raise ValueError("candidate and evidence must be dictionaries")

    candidate_gtin = (candidate.get("metadata") or {}).get("gtin")
    evidence_gtin = evidence.get("gtin")
    if not is_valid_gtin(candidate_gtin) or not is_valid_gtin(evidence_gtin):
        return {
            "status": "rejected",
            "reason": "validated_gtin_required",
            "candidate": candidate,
            "commerce_authorized": False,
        }
    if normalize_gtin(candidate_gtin) != normalize_gtin(evidence_gtin):
        return {
            "status": "rejected",
            "reason": "identity_mismatch",
            "candidate": candidate,
            "commerce_authorized": False,
        }

    source_kind = str(evidence.get("source_kind") or "").strip()
    source_ref = str(evidence.get("source_ref") or "").strip()
    observed_at = str(evidence.get("observed_at") or "").strip()
    if source_kind not in ALLOWED_SOURCE_KINDS or not source_ref or not observed_at:
        return {
            "status": "rejected",
            "reason": "invalid_provenance",
            "candidate": candidate,
            "commerce_authorized": False,
        }

    if any(evidence.get(field) is None for field in PHYSICAL_FIELDS):
        return {
            "status": "rejected",
            "reason": "physical_evidence_incomplete",
            "candidate": candidate,
            "commerce_authorized": False,
        }

    physical = {field: evidence[field] for field in PHYSICAL_FIELDS}
    policy = evaluate_initial_physical_fit(physical)

    updated = deepcopy(candidate)
    updated.setdefault("evaluation", {})["physical"] = {
        **physical,
        "policy": policy,
    }
    updated.setdefault("metadata", {})["physical_evidence"] = {
        "version": ENRICHMENT_VERSION,
        "gtin": normalize_gtin(evidence_gtin),
        "source_kind": source_kind,
        "source_ref": source_ref,
        "observed_at": observed_at,
    }

    return {
        "status": "enriched",
        "candidate": updated,
        "physical_policy": policy,
        "commerce_authorized": False,
        "external_action_authorized": False,
    }
