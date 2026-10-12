from __future__ import annotations


def acquire_cost_evidence(
    candidate: dict,
    *,
    freight_provider,
    destination_country: str = "US",
    quantity: int = 1,
) -> dict:
    enriched = dict(candidate)
    evidence = dict(enriched.get("cost_evidence") or {})
    shipping = freight_provider.fetch_shipping_evidence(
        enriched,
        destination_country=destination_country,
        quantity=quantity,
    )

    if shipping.get("status") == "known":
        enriched["supplier_shipping"] = float(shipping["shipping_cost"])
        evidence["supplier_shipping"] = {
            "status": "known",
            "source": str(shipping.get("source") or "cj-freight-calculate"),
            "currency": shipping.get("currency"),
            "variant_id": shipping.get("variant_id"),
            "origin_country": shipping.get("origin_country"),
            "destination_country": shipping.get("destination_country"),
            "logistic_name": shipping.get("logistic_name"),
            "logistic_aging": shipping.get("logistic_aging"),
        }
        status = "shipping_evidence_acquired"
    else:
        current = evidence.get("supplier_shipping")
        if not isinstance(current, dict) or current.get("status") != "known":
            evidence["supplier_shipping"] = {
                "status": "unknown",
                "source": str(shipping.get("source") or "cj-freight-calculate"),
                "reason": shipping.get("reason"),
                "destination_country": shipping.get("destination_country"),
            }
        status = "shipping_evidence_unavailable"

    enriched["cost_evidence"] = evidence
    metadata = dict(enriched.get("metadata") or {})
    metadata["shipping_evidence"] = shipping
    enriched["metadata"] = metadata

    return {
        "status": status,
        "candidate": enriched,
        "shipping_evidence": shipping,
        "commerce_external_writes": False,
        "live_execution_allowed": False,
    }
