from __future__ import annotations

from .token_readiness import assess_token_readiness


def build_provider_onboarding_status() -> dict:
    readiness = assess_token_readiness()

    steps = [
        {
            "provider": "cj",
            "credential_ready": readiness["cj"]["ready"],
            "accepted_modes": [
                "CJ_ACCESS_TOKEN",
                "CJ_API_KEY",
                "CJ_REFRESH_TOKEN",
            ],
        },
        {
            "provider": "ebay",
            "credential_ready": readiness["ebay"]["ready"],
            "accepted_modes": [
                "EBAY_ACCESS_TOKEN",
                "EBAY_CLIENT_ID + EBAY_CLIENT_SECRET",
            ],
        },
    ]

    return {
        "status": "provider_onboarding_ready",
        "all_credentials_ready": readiness["all_ready"],
        "steps": steps,
        "next_action": (
            "run_provider_handshake"
            if readiness["all_ready"]
            else "configure_missing_credentials"
        ),
        "secret_values_exposed": False,
        "live_execution_allowed": False,
    }
