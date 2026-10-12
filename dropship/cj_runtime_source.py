from __future__ import annotations

import os

from .cj_provider import CJDropshippingProductProvider
from .cj_token import CJAccessTokenProvider
from .token_readiness import assess_token_readiness


def build_cj_runtime_source() -> dict:
    readiness = assess_token_readiness()
    cj = readiness["cj"]
    if not cj["ready"]:
        return {
            "status": "setup_required",
            "reason": "cj_credentials_missing",
            "token_readiness": cj,
            "supplier_provider": None,
            "live_execution_allowed": False,
        }

    token = os.environ.get("CJ_ACCESS_TOKEN", "").strip()
    if not token:
        token = CJAccessTokenProvider().get_token()

    supplier = CJDropshippingProductProvider(
        token=token,
        keyword=os.environ.get("DROPSHIP_SEARCH_KEYWORD") or None,
        country_code=os.environ.get("DROPSHIP_SUPPLIER_COUNTRY") or None,
        page_size=int(os.environ.get("DROPSHIP_CJ_PAGE_SIZE", "20")),
        max_pages=int(os.environ.get("DROPSHIP_CJ_MAX_PAGES", "1")),
    )
    return {
        "status": "ready",
        "reason": None,
        "token_readiness": cj,
        "supplier_provider": supplier,
        "secret_values_exposed": False,
        "live_execution_allowed": False,
    }
