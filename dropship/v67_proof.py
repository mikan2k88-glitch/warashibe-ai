from __future__ import annotations

from .actual_evidence_controller_v67 import run_actual_evidence_controller_v67
from .v65_proof import _KnownFreight
from .v66_proof import _Supplier
from .v62_proof import _MemoryPersistence, _RealMarket, _handshake


def build_v67_proof() -> dict:
    result = run_actual_evidence_controller_v67(
        _Supplier(),
        _RealMarket(),
        freight_provider=_KnownFreight(),
        persistence_client=_MemoryPersistence(),
        provider_handshake=_handshake(),
        available_capital=3000,
        supplier_currency="USD",
        target_currency="USD",
        budget={
            "max_supplier_items": 5,
            "max_market_queries": 5,
            "max_market_quotes_per_query": 10,
        },
        shadow_thresholds={
            "min_observations": 20,
            "min_observation_days": 7,
        },
        marketplace_id="EBAY_US",
        ebay_user_access_token="",
    )

    checks = {
        "official_fee_evidence_applied": result["fee_evidence"]["acquired_count"] >= 1,
        "official_terms_evidence_applied": result["terms_evidence"]["acquired_count"] >= 1,
        "user_oauth_fails_closed": result["ebay_user_oauth"]["status"] == "setup_required",
        "return_policy_not_assumed": result["ebay_user_oauth"]["return_policy_read_ready"] is False,
        "human_gate_remains_blocked": result["human_gate_ready_count"] == 0,
        "automatic_execution_disabled": result["automatic_execution"] is False,
        "live_execution_disabled": result["live_execution_allowed"] is False,
    }

    return {
        "proof_version": "6.7",
        "passed": all(checks.values()),
        "checks": checks,
        "result": result,
        "maturity_ceiling": "ebay_actual_evidence_user_oauth_pending",
        "live_execution_allowed": False,
    }


def build_v67_acceptance() -> dict:
    proof = build_v67_proof()
    return {
        "acceptance_version": "6.7",
        "passed": proof["passed"],
        "endpoint": "ebay_actual_evidence_ready",
        "human_gate_required": True,
        "automatic_execution": False,
        "live_execution_allowed": False,
    }
