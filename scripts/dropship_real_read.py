from __future__ import annotations

import json
import os

from dropship.cj_provider import CJDropshippingProductProvider
from dropship.cj_token import CJAccessTokenProvider
from dropship.ebay_market_provider import EbayBrowseMarketProvider
from dropship.ebay_token import EbayApplicationTokenProvider
from dropship.market_provider import FixtureMarketProvider
from dropship.provider import FixtureSupplierProvider
from dropship.operations_runner import run_persistent_real_shadow
from dropship.persistence_health import assess_persistence_environment
from dropship.supabase_rest import SupabaseRestClient
from dropship.token_readiness import assess_token_readiness


def fixture_supplier():
    return FixtureSupplierProvider([
        {
            "product_key": "fixture-1",
            "name": "Generic Home Organizer",
            "supplier": "fixture-supplier",
            "category": "home",
            "supplier_cost": 10,
            "supplier_shipping": 0,
            "delivery_days": 5,
            "inventory_confirmed": True,
            "supplier_allows_dropshipping": True,
            "platform_terms_confirmed": True,
            "supplier_reliable": True,
        }
    ])


def fixture_market():
    return FixtureMarketProvider({
        "Generic Home Organizer": [
            {"price": 20, "currency": "USD"},
            {"price": 21, "currency": "USD"},
            {"price": 22, "currency": "USD"},
        ]
    })


def build_sources():
    readiness = assess_token_readiness()
    cj_token = os.environ.get("CJ_ACCESS_TOKEN", "").strip()
    ebay_token = os.environ.get("EBAY_ACCESS_TOKEN", "").strip()

    if readiness["cj"]["ready"] and not cj_token:
        cj_token = CJAccessTokenProvider().get_token()

    if readiness["ebay"]["ready"] and not ebay_token:
        ebay_token = EbayApplicationTokenProvider(
            environment=os.environ.get("EBAY_ENVIRONMENT", "production"),
        ).get_token()

    if cj_token and ebay_token:
        return (
            CJDropshippingProductProvider(
                token=cj_token,
                keyword=os.environ.get("DROPSHIP_SEARCH_KEYWORD") or None,
                country_code=os.environ.get("DROPSHIP_SUPPLIER_COUNTRY") or None,
                page_size=int(os.environ.get("DROPSHIP_CJ_PAGE_SIZE", "10")),
                max_pages=int(os.environ.get("DROPSHIP_CJ_MAX_PAGES", "1")),
            ),
            EbayBrowseMarketProvider(
                token=ebay_token,
                marketplace_id=os.environ.get("EBAY_MARKETPLACE_ID", "EBAY_US"),
                limit=int(os.environ.get("DROPSHIP_EBAY_LIMIT", "10")),
            ),
            "real_read",
        )

    if readiness["all_ready"]:
        raise RuntimeError("real-read credentials are configured but access tokens could not be resolved")

    return fixture_supplier(), fixture_market(), "fixture_proof"


def build_persistence_client():
    health = assess_persistence_environment()
    if health["status"] != "ready":
        return None
    return SupabaseRestClient()


def main():
    supplier, market, mode = build_sources()
    persistence_client = build_persistence_client()
    result = run_persistent_real_shadow(
        supplier,
        market,
        persistence_client=persistence_client,
        supplier_currency=os.environ.get("DROPSHIP_SUPPLIER_CURRENCY", "USD"),
        target_currency=os.environ.get("DROPSHIP_TARGET_CURRENCY", "USD"),
        budget={
            "max_supplier_items": int(os.environ.get("DROPSHIP_MAX_SUPPLIER_ITEMS", "5")),
            "max_market_queries": int(os.environ.get("DROPSHIP_MAX_MARKET_QUERIES", "5")),
            "max_market_quotes_per_query": int(os.environ.get("DROPSHIP_MAX_QUOTES", "10")),
        },
        shadow_thresholds={
            "min_observations": int(os.environ.get("DROPSHIP_SHADOW_MIN_OBSERVATIONS", "20")),
            "min_observation_days": int(os.environ.get("DROPSHIP_SHADOW_MIN_DAYS", "7")),
        },
        mode=mode,
    )
    output = {
        "mode": mode,
        "result": result,
        "live_execution_allowed": False,
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    if result["status"] == "blocked":
        raise SystemExit(1)
    if output["live_execution_allowed"]:
        raise SystemExit("live execution must remain disabled")


if __name__ == "__main__":
    main()
