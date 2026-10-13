from __future__ import annotations

from .release import CAPABILITIES
from .v66_proof import build_v66_acceptance, build_v66_proof


def build_v66_release_status() -> dict:
    proof = build_v66_proof()
    acceptance = build_v66_acceptance()
    return {
        "release": "dropshipping-warashibe-v6.6-fee-terms-evidence",
        "status": (
            "fee_terms_evidence_endpoint_reached"
            if proof["passed"] and acceptance["passed"]
            else "blocked"
        ),
        "proof_passed": proof["passed"],
        "acceptance_passed": acceptance["passed"],
        "capabilities": {
            **CAPABILITIES,
            "fee_evidence_v66": True,
            "terms_evidence_v66": True,
            "actual_evidence_controller_v66": True,
        },
        "maturity_ceiling": "fee_terms_evidence_human_gate",
        "human_gate_required": True,
        "automatic_execution_enabled": False,
        "external_writes_enabled": False,
        "live_execution_allowed": False,
    }
