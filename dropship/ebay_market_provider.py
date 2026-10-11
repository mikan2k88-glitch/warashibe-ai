from __future__ import annotations

import os

import requests


EBAY_SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"


def normalize_ebay_item(row: dict) -> dict | None:
    price = row.get("price") or {}
    try:
        value = float(price.get("value") or 0)
    except (TypeError, ValueError):
        return None
    currency = str(price.get("currency") or "")
    if value <= 0 or not currency:
        return None
    return {
        "market": "ebay",
        "item_id": row.get("itemId"),
        "title": row.get("title"),
        "price": value,
        "currency": currency,
        "condition": row.get("condition"),
        "item_url": row.get("itemWebUrl"),
        "seller_username": (row.get("seller") or {}).get("username"),
    }


class EbayBrowseMarketProvider:
    provider_name = "ebay-browse"

    def __init__(
        self,
        *,
        token: str | None = None,
        token_env: str = "EBAY_ACCESS_TOKEN",
        marketplace_id: str = "EBAY_US",
        timeout: int = 30,
        limit: int = 20,
    ):
        self.token = token or os.environ.get(token_env, "")
        self.marketplace_id = marketplace_id
        self.timeout = int(timeout)
        self.limit = min(200, max(1, int(limit)))

    def search(self, query: str) -> list[dict]:
        if not self.token:
            raise RuntimeError("eBay access token is not configured")
        response = requests.get(
            EBAY_SEARCH_URL,
            headers={
                "Authorization": f"Bearer {self.token}",
                "X-EBAY-C-MARKETPLACE-ID": self.marketplace_id,
            },
            params={"q": query, "limit": self.limit},
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        quotes = []
        for row in payload.get("itemSummaries") or []:
            if not isinstance(row, dict):
                continue
            normalized = normalize_ebay_item(row)
            if normalized:
                quotes.append(normalized)
        return quotes
