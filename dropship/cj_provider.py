from __future__ import annotations

import os
import re

import requests

from .provider import ReadOnlySupplierProvider


CJ_LIST_V2_URL = "https://developers.cjdropshipping.com/api2.0/v1/product/listV2"


def _delivery_days(value) -> int:
    text = str(value or "")
    numbers = [int(x) for x in re.findall(r"\d+", text)]
    return max(numbers) if numbers else 0


def normalize_cj_product(row: dict) -> dict:
    verified_inventory = int(row.get("totalVerifiedInventory") or 0)
    supplier_name = str(row.get("supplierName") or "CJdropshipping")
    cost = row.get("nowPrice") or row.get("discountPrice") or row.get("sellPrice") or 0
    try:
        cost = float(cost)
    except (TypeError, ValueError):
        cost = 0.0

    return {
        "product_key": str(row.get("id") or row.get("sku") or "unknown"),
        "name": str(row.get("nameEn") or row.get("sku") or "unknown"),
        "supplier": supplier_name,
        "category": str(row.get("threeCategoryName") or row.get("oneCategoryName") or "general"),
        "source": "cjdropshipping-list-v2",
        "supplier_cost": cost,
        "sale_price": 0.0,
        "supplier_shipping": 0.0,
        "delivery_days": _delivery_days(row.get("deliveryCycle")),
        "inventory_confirmed": verified_inventory > 0,
        "supplier_allows_dropshipping": False,
        "platform_terms_confirmed": False,
        "supplier_reliable": False,
        "cost_evidence": {
            "supplier_cost": {
                "status": "known" if cost > 0 else "unknown",
                "source": "cj-product-list-v2",
            },
            "supplier_shipping": {
                "status": "unknown",
                "source": "not_returned_by_product-list-v2",
            },
            "platform_fee_rate": {
                "status": "unknown",
                "source": "marketplace_specific",
            },
            "payment_fee_rate": {
                "status": "unknown",
                "source": "payment_path_specific",
            },
            "expected_return_cost": {
                "status": "unknown",
                "source": "return_terms_required",
            },
            "refund_reserve": {
                "status": "unknown",
                "source": "return_terms_required",
            },
        },
        "terms_evidence": {
            "supplier_dropshipping_permission": {
                "status": "unknown",
                "source": "terms_evidence_required",
            },
            "platform_terms": {
                "status": "unknown",
                "source": "marketplace_terms_required",
            },
            "return_terms": {
                "status": "unknown",
                "source": "return_terms_required",
            },
            "cancellation_terms": {
                "status": "unknown",
                "source": "cancellation_terms_required",
            },
        },
        "metadata": {
            "sku": row.get("sku"),
            "spu": row.get("spu"),
            "image": row.get("bigImage"),
            "listed_num": row.get("listedNum"),
            "verified_inventory": verified_inventory,
            "warehouse_inventory": row.get("warehouseInventoryNum"),
            "sale_status": row.get("saleStatus"),
            "authority_status": row.get("authorityStatus"),
            "currency": "USD",
        },
    }


class CJDropshippingProductProvider(ReadOnlySupplierProvider):
    provider_name = "cjdropshipping-list-v2"

    def __init__(
        self,
        *,
        token: str | None = None,
        token_env: str = "CJ_ACCESS_TOKEN",
        keyword: str | None = None,
        country_code: str | None = None,
        page_size: int = 20,
        max_pages: int = 3,
        timeout: int = 30,
    ):
        self.token = token or os.environ.get(token_env, "")
        self.keyword = keyword
        self.country_code = country_code
        self.page_size = min(100, max(1, int(page_size)))
        self.max_pages = max(1, int(max_pages))
        self.timeout = int(timeout)

    def fetch_offers(self) -> list[dict]:
        if not self.token:
            raise RuntimeError("CJ access token is not configured")

        offers = []
        for page in range(1, self.max_pages + 1):
            params = {"page": page, "size": self.page_size, "features": "enable_category"}
            if self.keyword:
                params["keyWord"] = self.keyword
            if self.country_code:
                params["countryCode"] = self.country_code

            response = requests.get(
                CJ_LIST_V2_URL,
                headers={"CJ-Access-Token": self.token},
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            data = payload.get("data") or {}
            content = data.get("content") or []

            page_rows = []
            for group in content:
                if not isinstance(group, dict):
                    continue
                for row in group.get("productList") or []:
                    if isinstance(row, dict):
                        page_rows.append(normalize_cj_product(row))
            offers.extend(page_rows)

            total_pages = int(data.get("totalPages") or page)
            if page >= total_pages:
                break

        return offers
