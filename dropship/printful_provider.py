from __future__ import annotations

import os

import requests

from .provider import ReadOnlySupplierProvider


PRINTFUL_PRODUCTS_URL = "https://api.printful.com/products"


def normalize_printful_product(row: dict) -> dict:
    return {
        "product_key": str(row.get("id") or "unknown"),
        "name": str(row.get("title") or "unknown"),
        "supplier": "Printful",
        "category": str(row.get("type_name") or row.get("type") or "general"),
        "source": "printful-catalog",
        "sale_price": 0.0,
        "supplier_cost": 0.0,
        "supplier_shipping": 0.0,
        "delivery_days": 0,
        "inventory_confirmed": False,
        "supplier_allows_dropshipping": False,
        "platform_terms_confirmed": False,
        "supplier_reliable": False,
        "metadata": {
            "brand": row.get("brand"),
            "model": row.get("model"),
            "image": row.get("image"),
            "variant_count": row.get("variant_count"),
            "currency": row.get("currency"),
            "is_discontinued": row.get("is_discontinued"),
            "provider_stage": "catalog_discovery",
        },
    }


class PrintfulCatalogProvider(ReadOnlySupplierProvider):
    provider_name = "printful-catalog"

    def __init__(
        self,
        *,
        token: str | None = None,
        token_env: str = "PRINTFUL_TOKEN",
        category_id: str | None = None,
        timeout: int = 30,
    ):
        self.token = token or os.environ.get(token_env, "")
        self.category_id = category_id
        self.timeout = int(timeout)

    def fetch_offers(self) -> list[dict]:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        params = {}
        if self.category_id:
            params["category_id"] = self.category_id

        response = requests.get(
            PRINTFUL_PRODUCTS_URL,
            headers=headers,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        rows = payload.get("result") or []
        return [
            normalize_printful_product(row)
            for row in rows
            if isinstance(row, dict)
        ]
