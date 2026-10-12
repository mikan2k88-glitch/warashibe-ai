from __future__ import annotations


FEE_FIELDS = (
    "platform_fee_rate",
    "payment_fee_rate",
    "expected_return_cost",
    "refund_reserve",
)


class UnknownFeeEvidenceProvider:
    provider_name = "fee-evidence-pending"

    def fetch_fee_evidence(self, candidate: dict) -> dict:
        return {
            "status": "unknown",
            "reason": "verified_fee_source_not_configured",
            "live_execution_allowed": False,
        }


def acquire_fee_evidence(candidate: dict, *, fee_provider) -> dict:
    enriched = dict(candidate)
    evidence = dict(enriched.get("cost_evidence") or {})
    result = fee_provider.fetch_fee_evidence(enriched)

    acquired = 0
    if result.get("status") == "known":
        for field in FEE_FIELDS:
            item = result.get(field)
            if not isinstance(item, dict):
                continue
            status = str(item.get("status") or "").strip().lower()
            if status not in {"known", "confirmed", "not_applicable"}:
                continue
            if "value" not in item:
                continue

            enriched[field] = item.get("value")
            evidence[field] = {
                key: value
                for key, value in item.items()
                if key != "value"
            }
            evidence[field]["status"] = status
            acquired += 1

    enriched["cost_evidence"] = evidence
    metadata = dict(enriched.get("metadata") or {})
    metadata["fee_evidence"] = {
        "provider": getattr(fee_provider, "provider_name", "unknown"),
        "status": result.get("status"),
        "reason": result.get("reason"),
        "acquired_fields": acquired,
    }
    enriched["metadata"] = metadata

    return {
        "status": "fee_evidence_acquired" if acquired else "fee_evidence_unavailable",
        "candidate": enriched,
        "provider_status": result.get("status"),
        "acquired_fields": acquired,
        "commerce_external_writes": False,
        "live_execution_allowed": False,
    }
