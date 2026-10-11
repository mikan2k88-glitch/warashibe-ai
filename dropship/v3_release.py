from __future__ import annotations

from .release import CAPABILITIES
from .v3_proof import build_v3_acceptance, build_v3_proof


def build_v3_release_status() -> dict:
    proof = build_v3_proof()
    acceptance = build_v3_acceptance()
    capabilities = {
        **CAPABILITIES,
        "v3_real_read_proof": True,
        "v3_real_read_acceptance": True,
        "real_provider_shadow_evidence": True,
    }
    return {
        "release": "dropshipping-warashibe-v3.0-real-read-shadow",
        "status": (
            "real_read_shadow_endpoint_reached"
            if proof["passed"] and acceptance["passed"]
            else "blocked"
        ),
        "proof_passed": proof["passed"],
        "acceptance_passed": acceptance["passed"],
        "capabilities": capabilities,
        "maturity_ceiling": "promotion_review_human_gate",
        "real_supplier_tokens_required_for_external_read": True,
        "commerce_external_writes_enabled": False,
        "live_execution_allowed": False,
    }
