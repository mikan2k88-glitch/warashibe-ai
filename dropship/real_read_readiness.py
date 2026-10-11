from __future__ import annotations

from .run_quality import assess_run_quality


def assess_real_read_readiness(
    run_result: dict,
    *,
    credential_health: dict | None = None,
    shadow_days: int = 0,
    shadow_observations: int = 0,
) -> dict:
    quality = assess_run_quality(run_result)
    credentials = credential_health or {
        "all_configured": False,
        "configured_count": 0,
        "required_count": 0,
    }
    checks = {
        "run_quality_passed": quality["passed"],
        "credentials_configured": credentials.get("all_configured") is True,
        "shadow_observations_started": int(shadow_observations) > 0,
        "shadow_days_started": int(shadow_days) > 0,
        "commerce_writes_disabled": run_result.get("commerce_external_writes") is False,
        "live_execution_disabled": run_result.get("live_execution_allowed") is False,
    }
    ready = all(checks.values())
    return {
        "status": "real_read_shadow_ready" if ready else "real_read_setup_incomplete",
        "ready": ready,
        "checks": checks,
        "run_quality": quality,
        "next_stage": "shadow_evidence_collection" if ready else "provider_setup",
        "live_execution_allowed": False,
    }
