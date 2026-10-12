from __future__ import annotations

import os

from .cj_provider import CJDropshippingProductProvider
from .cj_token import CJAccessTokenProvider
from .ebay_market_provider import EbayBrowseMarketProvider
from .ebay_token import EbayApplicationTokenProvider
from .token_readiness import assess_token_readiness


def build_real_runtime_sources() -> dict:
    readiness = assess_token_readiness()
    if not readiness["all_ready"]:
        return {
            "status": "setup_required",
            "reason": "real_provider_credentials_missing",
            "token_readiness": readiness,
            "supplier_provider": None,
            "market_provider": None,
        }

    cj_token = os.environ.get("CJ_ACCESS_TOKEN", "").strip()
    ebay_token = os.environ.get("EBAY_ACCESS_TOKEN", "").strip()

    if not cj_token:
        cj_token = CJAccessTokenProvider().get_token()

    if not ebay_token:
        ebay_token = EbayApplicationTokenProvider(
            environment=os.environ.get("EBAY_ENVIRONMENT", "production"),
        ).get_token()

    supplier = CJDropshippingProductProvider(
        token=cj_token,
        keyword=os.environ.get("DROPSHIP_SEARCH_KEYWORD") or None,
        country_code=os.environ.get("DROPSHIP_SUPPLIER_COUNTRY") or None,
        page_size=int(os.environ.get("DROPSHIP_CJ_PAGE_SIZE", "10")),
        max_pages=int(os.environ.get("DROPSHIP_CJ_MAX_PAGES", "1")),
    )
    market = EbayBrowseMarketProvider(
        token=ebay_token,
        marketplace_id=os.environ.get("EBAY_MARKETPLACE_ID", "EBAY_US"),
        limit=int(os.environ.get("DROPSHIP_EBAY_LIMIT", "10")),
    )

    return {
        "status": "ready",
        "reason": None,
        "token_readiness": readiness,
        "supplier_provider": supplier,
        "market_provider": market,
        "secret_values_exposed": False,
        "live_execution_allowed": False,
    }
