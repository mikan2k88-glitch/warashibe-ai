from __future__ import annotations

from .release import CAPABILITIES
from .v67_proof import build_v67_acceptance, build_v67_proof


def build_v67_release_status() -> dict:
    proof = build_v67_proof()
    acceptance = build_v67_acceptance()
    return {
        "release": "dropshipping-warashibe-v6.7-ebay-actual-evidence",
        "status": (
            "ebay_actual_evidence_endpoint_reached"
            if proof["passed"] and acceptance["passed"]
            else "blocked"
        ),
        "proof_passed": proof["passed"],
        "acceptance_passed": acceptance["passed"],
        "capabilities": {
            **CAPABILITIES,
            "ebay_official_fee_evidence_v67": True,
            "ebay_official_terms_evidence_v67": True,
            "ebay_user_return_policy_reader_v67": True,
            "actual_evidence_controller_v67": True,
        },
        "maturity_ceiling": "ebay_actual_evidence_user_oauth_pending",
        "human_gate_required": True,
        "automatic_execution_enabled": False,
        "external_writes_enabled": False,
        "live_execution_allowed": False,
    }
