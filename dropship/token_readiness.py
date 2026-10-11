from __future__ import annotations

import os


def assess_token_readiness() -> dict:
    cj_static = bool(os.environ.get("CJ_ACCESS_TOKEN", "").strip())
    cj_dynamic = bool(
        os.environ.get("CJ_API_KEY", "").strip()
        or os.environ.get("CJ_REFRESH_TOKEN", "").strip()
    )
    ebay_static = bool(os.environ.get("EBAY_ACCESS_TOKEN", "").strip())
    ebay_dynamic = bool(
        os.environ.get("EBAY_CLIENT_ID", "").strip()
        and os.environ.get("EBAY_CLIENT_SECRET", "").strip()
    )

    return {
        "cj": {
            "static_access_token": cj_static,
            "dynamic_token_credentials": cj_dynamic,
            "ready": cj_static or cj_dynamic,
        },
        "ebay": {
            "static_access_token": ebay_static,
            "dynamic_token_credentials": ebay_dynamic,
            "ready": ebay_static or ebay_dynamic,
        },
        "all_ready": (cj_static or cj_dynamic) and (ebay_static or ebay_dynamic),
        "secret_values_exposed": False,
        "live_execution_allowed": False,
    }
