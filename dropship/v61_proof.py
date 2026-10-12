from __future__ import annotations

from copy import deepcopy

from .v52_proof import build_v52_proof
from .v61_real_gate import build_v61_real_gate


def _real_review() -> dict:
    review = deepcopy(build_v52_proof()["review"])
    review["review"]["candidate"]["supplier"] = "cjdropshipping-list-v2"
    return review


def _real_observations(product_key: str) -> list[dict]:
    rows = []
    for day in range(1, 8):
        for index in range(3):
            rows.append({
                "product_key": product_key,
                "supplier": "cjdropshipping-list-v2",
                "source": "real-read-opportunity",
                "mode": "real_read",
                "sale_price": 20 + (index * 0.5),
                "supplier_cost": 8.0 + (0.05 * index),
                "inventory_confirmed": True,
                "expected_net_profit": 5.0 + index,
                "observed_at": f"2026-10-{day:02d}T0{index}:00:00+00:00",
            })
    return rows


def _real_runs() -> list[dict]:
    return [{
        "mode": "real_read",
        "supplier_provider": "cjdropshipping-list-v2",
        "market_provider": "ebay-browse",
        "observed_at": "2026-10-12T00:00:00+00:00",
    }]


def _handshake() -> dict:
    return {
        "status": "real_provider_handshake_ready",
        "successful_provider_count": 2,
    }


def build_v61_proof() -> dict:
    fixture_review = build_v52_proof()["review"]
    fixture = build_v61_real_gate(
        fixture_review,
        observations=_real_observations(fixture_review["product_key"]),
        recent_runs=_real_runs(),
        persistence_enabled=True,
        provider_handshake=_handshake(),
    )

    real_review = _real_review()
    real_gate = build_v61_real_gate(
        real_review,
        observations=_real_observations(real_review["product_key"]),
        recent_runs=_real_runs(),
        persistence_enabled=True,
        provider_handshake=_handshake(),
    )

    missing_persistence = build_v61_real_gate(
        real_review,
        observations=_real_observations(real_review["product_key"]),
        recent_runs=_real_runs(),
        persistence_enabled=False,
        provider_handshake=_handshake(),
    )

    checks = {
        "fixture_review_blocked": fixture["status"] == "blocked",
        "fixture_detected": fixture["qualification"]["fixture_detected"] is True,
        "real_evidence_qualified": real_gate["qualification"]["qualified"] is True,
        "real_gate_ready": real_gate["status"] == "real_evidence_human_gate_ready",
        "persistence_required": missing_persistence["status"] == "blocked",
        "human_gate_required": real_gate["human_gate_required"] is True,
        "automatic_execution_disabled": real_gate["automatic_execution"] is False,
        "external_write_disabled": real_gate["external_write_enabled"] is False,
        "live_execution_disabled": real_gate["live_execution_allowed"] is False,
    }

    return {
        "proof_version": "6.1",
        "passed": all(checks.values()),
        "checks": checks,
        "fixture_case": fixture,
        "real_case": real_gate,
        "missing_persistence_case": missing_persistence,
        "maturity_ceiling": "real_evidence_human_gate",
        "live_execution_allowed": False,
    }


def build_v61_acceptance() -> dict:
    proof = build_v61_proof()
    checks = {
        "proof_passed": proof["passed"],
        "fixture_blocked": proof["fixture_case"]["status"] == "blocked",
        "real_case_ready": proof["real_case"]["status"] == "real_evidence_human_gate_ready",
        "human_control_preserved": proof["real_case"]["human_gate_required"] is True,
        "live_execution_disabled": proof["live_execution_allowed"] is False,
    }
    return {
        "acceptance_version": "6.1",
        "passed": all(checks.values()),
        "checks": checks,
        "endpoint": "real_evidence_human_gate",
        "next_phase": "collect_actual_provider_evidence",
        "live_execution_allowed": False,
    }
