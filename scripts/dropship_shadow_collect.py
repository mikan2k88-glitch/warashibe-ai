from __future__ import annotations

import json
import os

from dropship.provider import FixtureSupplierProvider, HttpJsonSupplierProvider
from dropship.shadow_collector import collect_shadow_observations


def build_provider():
    url = os.environ.get("DROPSHIP_PROVIDER_URL", "").strip()
    if url:
        return HttpJsonSupplierProvider(
            url,
            provider_name=os.environ.get("DROPSHIP_PROVIDER_NAME", "configured-http-json"),
            timeout=int(os.environ.get("DROPSHIP_PROVIDER_TIMEOUT", "30")),
        )
    return FixtureSupplierProvider([
        {
            "product_key": "scheduled-proof",
            "name": "scheduled-proof",
            "sale_price": 3000,
            "supplier_cost": 1200,
            "supplier_shipping": 200,
            "delivery_days": 5,
            "inventory_confirmed": True,
        }
    ])


def main():
    result = collect_shadow_observations(
        build_provider(),
        max_items=int(os.environ.get("DROPSHIP_PROVIDER_MAX_ITEMS", "200")),
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if result["status"] == "blocked":
        raise SystemExit(1)
    if result["live_execution_allowed"]:
        raise SystemExit("live execution must remain disabled")


if __name__ == "__main__":
    main()
