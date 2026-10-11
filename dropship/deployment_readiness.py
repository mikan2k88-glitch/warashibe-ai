from __future__ import annotations

import os

from .credential_health import check_credential_env
from .persistence_health import assess_persistence_environment


def assess_deployment_readiness() -> dict:
    real_read = check_credential_env(["CJ_ACCESS_TOKEN", "EBAY_ACCESS_TOKEN"])
    persistence = assess_persistence_environment()
    dll_url = bool(os.environ.get("DLL_CONCIERGE_BASE_URL", "").strip())

    checks = {
        "real_read_credentials": real_read["all_configured"],
        "persistence_ready": persistence["status"] == "ready",
        "dll_url_configured_or_default": True,
    }

    if checks["real_read_credentials"] and checks["persistence_ready"]:
        mode = "real_read_persistent_shadow"
    elif checks["real_read_credentials"]:
        mode = "real_read_ephemeral_shadow"
    else:
        mode = "fixture_proof"

    return {
        "status": "deployment_readiness_ready",
        "mode": mode,
        "checks": checks,
        "credential_health": real_read,
        "persistence_health": persistence,
        "dll_base_url_explicit": dll_url,
        "commerce_external_writes_enabled": False,
        "live_execution_allowed": False,
    }
