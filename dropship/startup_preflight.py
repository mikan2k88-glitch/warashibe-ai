from __future__ import annotations

from .deployment_readiness import assess_deployment_readiness
from .provider_catalog import list_provider_catalog


def build_startup_preflight() -> dict:
    readiness = assess_deployment_readiness()
    providers = list_provider_catalog()

    warnings = []
    if readiness["mode"] == "fixture_proof":
        warnings.append("real_read_credentials_not_configured")
    if readiness["persistence_health"]["status"] != "ready":
        warnings.append("persistent_shadow_history_not_configured")

    return {
        "status": "startup_preflight_ready",
        "mode": readiness["mode"],
        "readiness": readiness,
        "provider_catalog": providers,
        "warnings": warnings,
        "safe_to_start_research_runtime": True,
        "safe_to_start_live_commerce": False,
        "live_execution_allowed": False,
    }
