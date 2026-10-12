from __future__ import annotations


TERM_FIELDS = (
    "supplier_dropshipping_permission",
    "platform_terms",
    "return_terms",
    "cancellation_terms",
)


class UnknownTermsEvidenceProvider:
    provider_name = "terms-evidence-pending"

    def fetch_terms_evidence(self, candidate: dict) -> dict:
        return {
            "status": "unknown",
            "reason": "verified_terms_source_not_configured",
            "live_execution_allowed": False,
        }


def acquire_terms_evidence(candidate: dict, *, terms_provider) -> dict:
    enriched = dict(candidate)
    evidence = dict(enriched.get("terms_evidence") or {})
    result = terms_provider.fetch_terms_evidence(enriched)

    acquired = 0
    if result.get("status") == "known":
        for field in TERM_FIELDS:
            item = result.get(field)
            if not isinstance(item, dict):
                continue
            status = str(item.get("status") or "").strip().lower()
            if status not in {"confirmed", "known", "accepted"}:
                continue
            evidence[field] = dict(item)
            evidence[field]["status"] = status
            acquired += 1

    enriched["terms_evidence"] = evidence
    enriched["supplier_allows_dropshipping"] = (
        (evidence.get("supplier_dropshipping_permission") or {}).get("status")
        in {"confirmed", "known", "accepted"}
    )
    enriched["platform_terms_confirmed"] = (
        (evidence.get("platform_terms") or {}).get("status")
        in {"confirmed", "known", "accepted"}
    )
    enriched["return_terms_confirmed"] = (
        (evidence.get("return_terms") or {}).get("status")
        in {"confirmed", "known", "accepted"}
    )
    enriched["cancellation_terms_confirmed"] = (
        (evidence.get("cancellation_terms") or {}).get("status")
        in {"confirmed", "known", "accepted"}
    )

    metadata = dict(enriched.get("metadata") or {})
    metadata["terms_evidence_acquisition"] = {
        "provider": getattr(terms_provider, "provider_name", "unknown"),
        "status": result.get("status"),
        "reason": result.get("reason"),
        "acquired_fields": acquired,
    }
    enriched["metadata"] = metadata

    return {
        "status": "terms_evidence_acquired" if acquired else "terms_evidence_unavailable",
        "candidate": enriched,
        "provider_status": result.get("status"),
        "acquired_fields": acquired,
        "commerce_external_writes": False,
        "live_execution_allowed": False,
    }
