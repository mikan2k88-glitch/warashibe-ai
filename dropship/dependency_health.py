from __future__ import annotations


def build_dependency_health(*, dll_status: str = "unknown", provider_count: int = 0) -> dict:
    dll_ok = dll_status in {"ok", "degraded"}
    provider_ok = int(provider_count) > 0
    overall = "healthy" if dll_status == "ok" and provider_ok else "degraded"
    if not provider_ok:
        overall = "blocked"

    return {
        "status": overall,
        "dependencies": {
            "dll_concierge": dll_status,
            "supplier_providers_registered": int(provider_count),
        },
        "research_can_continue_without_dll_live": provider_ok,
        "live_execution_allowed": False,
    }
