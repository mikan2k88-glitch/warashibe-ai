"""Read-only Yahoo! Shopping item-search connector for PG-012.

This module supports only Yahoo! Shopping V3 itemSearch GET requests. It does
not place orders, create payments, modify accounts, or perform commerce.
Credentials are injected by caller/environment and are never returned.
"""

import json
import os
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from research_lab.live_market_evidence_ingestion import ingest_records
from research_lab.real_market_adapter import observation_to_candidate

YAHOO_ITEM_SEARCH_URL = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"
CONNECTOR_VERSION = "0.1"


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Yahoo Shopping redirect refused")


def build_item_search_request(query, appid, *, results=20, condition=None):
    query = str(query or "").strip()
    appid = str(appid or "").strip()
    if not query:
        raise ValueError("query is required")
    if not appid:
        raise ValueError("Yahoo! Shopping app ID is required")
    if isinstance(results, bool):
        raise ValueError("results must be between 1 and 100")
    results = int(results)
    if not 1 <= results <= 100:
        raise ValueError("results must be between 1 and 100")
    if condition not in (None, "new", "used"):
        raise ValueError("condition must be new or used")

    params = {"appid": appid, "query": query, "results": results}
    if condition is not None:
        params["condition"] = condition

    url = YAHOO_ITEM_SEARCH_URL + "?" + urlencode(params)
    parts = urlsplit(url)
    if (
        parts.scheme != "https"
        or parts.netloc != "shopping.yahooapis.jp"
        or parts.path != "/ShoppingWebService/V3/itemSearch"
        or parts.username
        or parts.password
        or parts.fragment
    ):
        raise ValueError("Yahoo Shopping API destination refused")

    return Request(
        url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "warashibe-ai-research/0.1",
        },
    )


def fetch_item_search_payload(
    query,
    appid,
    *,
    results=20,
    condition=None,
    timeout=10,
):
    request = build_item_search_request(
        query,
        appid,
        results=results,
        condition=condition,
    )
    with build_opener(NoRedirectHandler()).open(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Yahoo Shopping response must be a JSON object")
    return payload


def yahoo_search_to_records(payload, *, observed_at=None):
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dictionary")
    hits = payload.get("hits") or []
    if not isinstance(hits, list):
        raise TypeError("hits must be a list")

    records, rejected = [], []
    for index, hit in enumerate(hits):
        try:
            if not isinstance(hit, dict):
                raise TypeError("hit must be a dictionary")
            code = str(hit.get("code") or "").strip()
            name = str(hit.get("name") or "").strip()
            price = hit.get("price")
            if not code or not name:
                raise ValueError("code and name are required")
            if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
                raise ValueError("price must be a non-negative number")

            genre = hit.get("genreCategory") or {}
            if not isinstance(genre, dict):
                genre = {}
            seller = hit.get("seller") or {}
            if not isinstance(seller, dict):
                seller = {}

            records.append({
                "external_id": code,
                "name": name,
                "category": str(genre.get("name") or "unknown"),
                "source": "yahoo_shopping",
                "source_url": hit.get("url"),
                "currency": "JPY",
                "purchase_price": float(price),
                # Search result price is asking-price evidence, not a realized sale.
                "expected_sale_price": float(price),
                "sale_probability": 0.0,
                "confidence": 0.0,
                "evidence_count": 1,
                "observed_at": observed_at,
                "metadata": {
                    "provider": "yahoo_shopping",
                    "connector_version": CONNECTOR_VERSION,
                    "condition": hit.get("condition"),
                    "seller_name": seller.get("name"),
                    "asking_price_only": True,
                    "gtin": hit.get("janCode") or None,
                    # The official item-search result does not guarantee parcel
                    # dimensions/weight, so PG-011 must fail closed until enriched.
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


def ingest_yahoo_shopping_payload(payload, *, observed_at=None):
    records, mapping_rejected = yahoo_search_to_records(
        payload,
        observed_at=observed_at,
    )
    ingestion = ingest_records("yahoo_shopping", records)
    # Mapping rejections are preserved in the normalized result contract by
    # appending them to rejected evidence.
    if mapping_rejected:
        from dataclasses import replace
        ingestion = replace(
            ingestion,
            rejected=tuple(mapping_rejected) + ingestion.rejected,
            raw_count=len(records) + len(mapping_rejected),
        )
    return ingestion


def fetch_and_ingest_yahoo_shopping(
    query,
    appid,
    *,
    results=20,
    condition=None,
    timeout=10,
    fetch_payload=fetch_item_search_payload,
    observed_at=None,
):
    payload = fetch_payload(
        query,
        appid,
        results=results,
        condition=condition,
        timeout=timeout,
    )
    return ingest_yahoo_shopping_payload(payload, observed_at=observed_at)


def fetch_and_ingest_yahoo_shopping_from_environment(
    query,
    *,
    environ=None,
    results=20,
    condition=None,
    timeout=10,
    fetch_payload=fetch_item_search_payload,
    observed_at=None,
):
    env = os.environ if environ is None else environ
    appid = str(env.get("YAHOO_SHOPPING_APP_ID") or "").strip()
    if not appid:
        raise RuntimeError("Yahoo! Shopping app ID is not configured")
    return fetch_and_ingest_yahoo_shopping(
        query,
        appid,
        results=results,
        condition=condition,
        timeout=timeout,
        fetch_payload=fetch_payload,
        observed_at=observed_at,
    )


def yahoo_observation_to_candidate(observation):
    if getattr(observation, "source", None) != "yahoo_shopping":
        raise ValueError("Yahoo Shopping observation required")
    return observation_to_candidate(observation)
