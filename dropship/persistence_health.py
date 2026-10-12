from __future__ import annotations

import os


def assess_persistence_environment() -> dict:
    url_present = bool(os.environ.get("SUPABASE_URL", "").strip())
    service_key_present = bool(
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.environ.get("SUPABASE_SECRET_KEY", "").strip()
        or os.environ.get("SUPABASE_KEY", "").strip()
    )
    return {
        "status": "ready" if url_present and service_key_present else "not_configured",
        "supabase_url_present": url_present,
        "server_secret_present": service_key_present,
        "secret_values_exposed": False,
        "append_only_mode": True,
        "live_execution_allowed": False,
    }
