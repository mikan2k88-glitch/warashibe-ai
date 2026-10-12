from __future__ import annotations

import json
import os

from dropship.cj_freight_provider import CJFreightEvidenceProvider
from dropship.cj_runtime_source import build_cj_runtime_source
from dropship.cost_evidence_acquisition import acquire_cost_evidence


def main():
    source = build_cj_runtime_source()
    if source["status"] != "ready":
        print(json.dumps({
            "status": "setup_required",
            "reason": source["reason"],
            "live_execution_allowed": False,
        }, ensure_ascii=False, sort_keys=True))
        return

    supplier = source["supplier_provider"]
    offers = list(supplier.fetch_offers())[:1]
    if not offers:
        print(json.dumps({
            "status": "no_candidate",
            "live_execution_allowed": False,
        }, ensure_ascii=False, sort_keys=True))
        return

    freight = CJFreightEvidenceProvider(token=getattr(supplier, "token", ""))
    result = acquire_cost_evidence(
        offers[0],
        freight_provider=freight,
        destination_country=os.environ.get("DROPSHIP_FREIGHT_DESTINATION", "US"),
        quantity=int(os.environ.get("DROPSHIP_FREIGHT_QUANTITY", "1")),
    )

    shipping = result.get("shipping_evidence") or {}
    print(json.dumps({
        "status": result.get("status"),
        "product_key": (result.get("candidate") or {}).get("product_key"),
        "shipping_evidence": {
            "status": shipping.get("status"),
            "source": shipping.get("source"),
            "shipping_cost": shipping.get("shipping_cost"),
            "currency": shipping.get("currency"),
            "variant_id": shipping.get("variant_id"),
            "origin_country": shipping.get("origin_country"),
            "destination_country": shipping.get("destination_country"),
            "logistic_name": shipping.get("logistic_name"),
            "logistic_aging": shipping.get("logistic_aging"),
            "reason": shipping.get("reason"),
        },
        "commerce_external_writes": False,
        "live_execution_allowed": False,
        "secret_values_exposed": False,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
