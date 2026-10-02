"""Read-only Rakuten Product Search connector for PG-013.

This module supports only Rakuten Product Search GET requests. It does not
purchase items, place orders, create payments, list products, or mutate accounts.
The access key is sent as an HTTP header so it is not embedded in request URLs.
"""

import json
import os
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from research_lab.live_market_evidence_ingestion import ingest_records

RAKUTEN_PRODUCT_SEARCH_URL = (
    "https://openapi.rakuten.co.jp/ichibaproduct/api/Product/Search/20250801"
)
CONNECTOR_VERSION = "0.1"


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Rakuten Product Search redirect refused")


def build_product_search_request(product_code, application_id, access_key, *, hits=20):
    product_code = str(product_code or "").strip()
    application_id = str(application_id or "").strip()
    access_key = str(access_key or "").strip()

    if not product_code:
        raise ValueError("product_code is required")
    if not application_id:
        raise ValueError("Rakuten application ID is required")
    if not access_key:
        raise ValueError("Rakuten access key is required")
    if isinstance(hits, bool):
        raise ValueError("hits must be between 1 and 30")
    hits = int(hits)
    if not 1 <= hits <= 30:
        raise ValueError("hits must be between 1 and 30")

    url = RAKUTEN_PRODUCT_SEARCH_URL + "?" + urlencode({
        "applicationId": application_id,
        "productCode": product_code,
        "hits": hits,
        "format": "json",
        "formatVersion": 2,
    })
    parts = urlsplit(url)
    if (
        parts.scheme != "https"
        or parts.netloc != "openapi.rakuten.co.jp"
        or parts.path != "/ichibaproduct/api/Product/Search/20250801"
        or parts.username
        or parts.password
        or parts.fragment
    ):
        raise ValueError("Rakuten Product Search destination refused")

    return Request(
        url,
        method="GET",
        headers={
            "Accept": "application/json",
            "accessKey": access_key,
            "User-Agent": "warashibe-ai-research/0.1",
        },
    )


def fetch_product_search_payload(
    product_code,
    application_id,
    access_key,
    *,
    hits=20,
    timeout=10,
):
    request = build_product_search_request(
        product_code,
        application_id,
        access_key,
        hits=hits,
    )
    with build_opener(NoRedirectHandler()).open(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Rakuten Product Search response must be a JSON object")
    return payload


def _price(item):
    for key in ("salesMinPrice", "minPrice", "averagePrice"):
        value = item.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)) and value >= 0:
            return float(value)
    raise ValueError("Rakuten product price is required")


def rakuten_product_to_records(payload, *, observed_at=None):
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dictionary")
    items = payload.get("items") or []
    if not isinstance(items, list):
        raise TypeError("items must be a list")

    records, rejected = [], []
    for index, item in enumerate(items):
        try:
            if not isinstance(item, dict):
                raise TypeError("item must be a dictionary")

            # Support both formatVersion=2 flat items and legacy wrapped items.
            if isinstance(item.get("item"), dict):
                item = item["item"]

            product_id = str(item.get("productId") or "").strip()
            product_code = str(item.get("productCode") or "").strip()
            product_name = str(item.get("productName") or "").strip()
            if not product_id or not product_code or not product_name:
                raise ValueError("productId, productCode, and productName are required")

            asking_price = _price(item)
            average_price = item.get("averagePrice")
            if isinstance(average_price, bool) or not isinstance(
                average_price, (int, float)
            ) or average_price < 0:
                average_price = asking_price

            records.append({
                "external_id": product_id,
                "name": product_name,
                "category": str(item.get("genreName") or "unknown"),
                "source": "rakuten_product",
                "source_url": item.get("productUrlPC"),
                "currency": "JPY",
                "purchase_price": asking_price,
                "expected_sale_price": float(average_price),
                "sale_probability": 0.0,
                "confidence": 0.0,
                "evidence_count": 1,
                "observed_at": observed_at,
                "metadata": {
                    "provider": "rakuten_product",
                    "connector_version": CONNECTOR_VERSION,
                    "gtin": product_code,
                    "model_number": item.get("productNo"),
                    "brand_name": item.get("brandName"),
                    "average_asking_price_jpy": float(average_price),
                    "asking_price_only": True,
                    "package_size_class": None,
                    "weight_grams": None,
                    "shipping_cost_jpy": None,
                    "fragility_score": None,
                    "storage_score": None,
                    "domestic_shipping": None,
                },
            })
        except (TypeError, ValueError) as exc:
            rejected.append({"index": index, "reason": str(exc)})
    return records, rejected


def ingest_rakuten_product_payload(payload, *, observed_at=None):
    records, mapping_rejected = rakuten_product_to_records(
        payload,
        observed_at=observed_at,
    )
    ingestion = ingest_records("rakuten_product", records)
    if mapping_rejected:
        from dataclasses import replace
        ingestion = replace(
            ingestion,
            rejected=tuple(mapping_rejected) + ingestion.rejected,
            raw_count=len(records) + len(mapping_rejected),
        )
    return ingestion


def fetch_and_ingest_rakuten_product(
    product_code,
    application_id,
    access_key,
    *,
    hits=20,
    timeout=10,
    fetch_payload=fetch_product_search_payload,
    observed_at=None,
):
    payload = fetch_payload(
        product_code,
        application_id,
        access_key,
        hits=hits,
        timeout=timeout,
    )
    return ingest_rakuten_product_payload(payload, observed_at=observed_at)


def fetch_and_ingest_rakuten_product_from_environment(
    product_code,
    *,
    environ=None,
    hits=20,
    timeout=10,
    fetch_payload=fetch_product_search_payload,
    observed_at=None,
):
    env = os.environ if environ is None else environ
    application_id = str(env.get("RAKUTEN_APPLICATION_ID") or "").strip()
    access_key = str(env.get("RAKUTEN_ACCESS_KEY") or "").strip()

    if not application_id:
        raise RuntimeError("Rakuten application ID is not configured")
    if not access_key:
        raise RuntimeError("Rakuten access key is not configured")

    return fetch_and_ingest_rakuten_product(
        product_code,
        application_id,
        access_key,
        hits=hits,
        timeout=timeout,
        fetch_payload=fetch_payload,
        observed_at=observed_at,
    )
