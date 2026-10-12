from __future__ import annotations


FIXTURE_MARKERS = {
    "fixture",
    "fixture-market",
    "fixture-supplier",
    "fixture_proof",
}


def qualify_real_evidence(
    review: dict,
    *,
    observations: list[dict],
    recent_runs: list[dict],
    persistence_enabled: bool,
    provider_handshake: dict | None = None,
) -> dict:
    product_key = str(review.get("product_key") or "")
    relevant = [
        row for row in observations
        if str(row.get("product_key") or "") == product_key
    ]

    sources = {
        str(row.get("source") or "").strip().lower()
        for row in relevant
        if row.get("source")
    }
    suppliers = {
        str(row.get("supplier") or "").strip().lower()
        for row in relevant
        if row.get("supplier")
    }
    modes = {
        str(row.get("mode") or "").strip().lower()
        for row in recent_runs
        if row.get("mode")
    }
    supplier_providers = {
        str(row.get("supplier_provider") or "").strip().lower()
        for row in recent_runs
        if row.get("supplier_provider")
    }
    market_providers = {
        str(row.get("market_provider") or "").strip().lower()
        for row in recent_runs
        if row.get("market_provider")
    }

    review_candidate = (review.get("review") or {}).get("candidate") or {}
    review_supplier = str(review_candidate.get("supplier") or "").strip().lower()

    fixture_detected = (
        review_supplier in FIXTURE_MARKERS
        or any(
        marker in sources
        or marker in suppliers
        or marker in modes
        or marker in supplier_providers
        or marker in market_providers
        for marker in FIXTURE_MARKERS
        )
    )

    real_read_observations = [
        row for row in relevant
        if str(row.get("source") or "").lower() == "real-read-opportunity"
    ]
    real_read_runs = [
        row for row in recent_runs
        if str(row.get("mode") or "").lower() == "real_read"
    ]

    handshake = provider_handshake or {}
    handshake_ok = (
        handshake.get("status") == "real_provider_handshake_ready"
        and int(handshake.get("successful_provider_count") or 0) >= 2
    )

    checks = {
        "promotion_review_ready": review.get("eligible_for_human_review") is True,
        "persistent_history_enabled": persistence_enabled is True,
        "real_read_observations_present": len(real_read_observations) > 0,
        "real_read_run_present": len(real_read_runs) > 0,
        "provider_handshake_ready": handshake_ok,
        "fixture_evidence_absent": fixture_detected is False,
    }
    qualified = all(checks.values())

    return {
        "qualification_version": "6.1",
        "status": "real_evidence_qualified" if qualified else "real_evidence_incomplete",
        "qualified": qualified,
        "product_key": product_key,
        "checks": checks,
        "evidence_counts": {
            "product_observations": len(relevant),
            "real_read_observations": len(real_read_observations),
            "recent_runs": len(recent_runs),
            "real_read_runs": len(real_read_runs),
        },
        "fixture_detected": fixture_detected,
        "human_gate_required": True,
        "automatic_execution": False,
        "external_write_enabled": False,
        "live_execution_allowed": False,
    }
