from __future__ import annotations


PROVIDERS = [
    {
        "name": "cjdropshipping-list-v2",
        "mode": "read_only",
        "auth": "CJ_ACCESS_TOKEN",
        "role": "supplier_product_discovery",
        "provides_supplier_cost": True,
        "provides_verified_inventory": True,
        "provides_target_sale_price": False,
        "live_order_capable_in_warashibe": False,
    },
    {
        "name": "printful-catalog",
        "mode": "read_only",
        "auth": "PRINTFUL_TOKEN_optional_for_catalog",
        "role": "catalog_discovery",
        "provides_supplier_cost": False,
        "provides_verified_inventory": False,
        "provides_target_sale_price": False,
        "live_order_capable_in_warashibe": False,
    },
    {
        "name": "http-json",
        "mode": "read_only",
        "auth": "configurable",
        "role": "generic_supplier_feed",
        "provides_supplier_cost": "depends_on_feed",
        "provides_verified_inventory": "depends_on_feed",
        "provides_target_sale_price": "depends_on_feed",
        "live_order_capable_in_warashibe": False,
    },
    {
        "name": "csv-feed",
        "mode": "read_only",
        "auth": "configurable",
        "role": "generic_supplier_feed",
        "provides_supplier_cost": "depends_on_feed",
        "provides_verified_inventory": "depends_on_feed",
        "provides_target_sale_price": "depends_on_feed",
        "live_order_capable_in_warashibe": False,
    },
]


def list_provider_catalog() -> dict:
    return {
        "status": "ok",
        "providers": list(PROVIDERS),
        "live_order_provider_enabled": False,
    }
