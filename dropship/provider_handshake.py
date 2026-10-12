from __future__ import annotations

from .cj_provider import CJDropshippingProductProvider
from .cj_token import CJAccessTokenProvider
from .ebay_market_provider import EbayBrowseMarketProvider
from .ebay_token import EbayApplicationTokenProvider


def run_cj_handshake(*, token_provider=None, keyword: str | None = None) -> dict:
    token_provider = token_provider or CJAccessTokenProvider()
    if not token_provider.configured():
        return {
            "provider": "cj",
            "status": "not_configured",
            "token_acquired": False,
            "read_succeeded": False,
            "live_execution_allowed": False,
        }

    try:
        token = token_provider.get_token()
        provider = CJDropshippingProductProvider(
            token=token,
            keyword=keyword,
            page_size=1,
            max_pages=1,
        )
        rows = provider.fetch_offers()
        return {
            "provider": "cj",
            "status": "ok",
            "token_acquired": True,
            "read_succeeded": True,
            "sample_count": len(rows),
            "sample_product_key": rows[0].get("product_key") if rows else None,
            "secret_values_exposed": False,
            "live_execution_allowed": False,
        }
    except Exception as exc:
        return {
            "provider": "cj",
            "status": "failed",
            "token_acquired": False,
            "read_succeeded": False,
            "error": str(exc),
            "secret_values_exposed": False,
            "live_execution_allowed": False,
        }


def run_ebay_handshake(*, token_provider=None, query: str = "home organizer") -> dict:
    token_provider = token_provider or EbayApplicationTokenProvider()
    if not token_provider.configured():
        return {
            "provider": "ebay",
            "status": "not_configured",
            "token_acquired": False,
            "read_succeeded": False,
            "live_execution_allowed": False,
        }

    try:
        token = token_provider.get_token()
        provider = EbayBrowseMarketProvider(
            token=token,
            limit=1,
        )
        rows = provider.search(query)
        return {
            "provider": "ebay",
            "status": "ok",
            "token_acquired": True,
            "read_succeeded": True,
            "sample_count": len(rows),
            "sample_title": rows[0].get("title") if rows else None,
            "secret_values_exposed": False,
            "live_execution_allowed": False,
        }
    except Exception as exc:
        return {
            "provider": "ebay",
            "status": "failed",
            "token_acquired": False,
            "read_succeeded": False,
            "error": str(exc),
            "secret_values_exposed": False,
            "live_execution_allowed": False,
        }


def run_provider_handshake(*, cj_token_provider=None, ebay_token_provider=None) -> dict:
    cj = run_cj_handshake(token_provider=cj_token_provider)
    ebay = run_ebay_handshake(token_provider=ebay_token_provider)

    configured = [row for row in (cj, ebay) if row["status"] != "not_configured"]
    successful = [row for row in configured if row["status"] == "ok"]

    return {
        "status": (
            "real_provider_handshake_ready"
            if len(successful) == 2
            else "real_provider_handshake_incomplete"
        ),
        "cj": cj,
        "ebay": ebay,
        "configured_provider_count": len(configured),
        "successful_provider_count": len(successful),
        "secret_values_exposed": False,
        "commerce_write_performed": False,
        "live_execution_allowed": False,
    }
