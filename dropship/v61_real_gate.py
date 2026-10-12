from __future__ import annotations

from .limited_live_gate_v60 import build_v60_gate
from .real_evidence_qualification import qualify_real_evidence


def build_v61_real_gate(
    review: dict,
    *,
    observations: list[dict],
    recent_runs: list[dict],
    persistence_enabled: bool,
    provider_handshake: dict | None = None,
) -> dict:
    qualification = qualify_real_evidence(
        review,
        observations=observations,
        recent_runs=recent_runs,
        persistence_enabled=persistence_enabled,
        provider_handshake=provider_handshake,
    )

    if not qualification["qualified"]:
        return {
            "gate_version": "6.1",
            "status": "blocked",
            "reason": "real_evidence_not_qualified",
            "qualification": qualification,
            "v60_gate": None,
            "human_gate_required": True,
            "automatic_execution": False,
            "external_write_enabled": False,
            "live_execution_allowed": False,
        }

    v60 = build_v60_gate(review)
    passed = qualification["qualified"] and v60["passed"]

    return {
        "gate_version": "6.1",
        "status": "real_evidence_human_gate_ready" if passed else "blocked",
        "passed": passed,
        "qualification": qualification,
        "v60_gate": v60,
        "human_gate_required": True,
        "automatic_execution": False,
        "external_write_enabled": False,
        "live_execution_allowed": False,
    }
