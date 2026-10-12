from __future__ import annotations

from .release import CAPABILITIES
from .v4_proof import build_v4_acceptance, build_v4_proof


def build_v4_release_status() -> dict:
    proof = build_v4_proof()
    acceptance = build_v4_acceptance()
    capabilities = {
        **CAPABILITIES,
        "v4_token_automation_proof": True,
        "v4_token_automation_acceptance": True,
        "server_side_token_minting": True,
    }
    return {
        "release": "dropshipping-warashibe-v4.0-token-automation",
        "status": (
            "token_automation_endpoint_reached"
            if proof["passed"] and acceptance["passed"]
            else "blocked"
        ),
        "proof_passed": proof["passed"],
        "acceptance_passed": acceptance["passed"],
        "capabilities": capabilities,
        "maturity_ceiling": "promotion_review_human_gate",
        "real_provider_credentials_required_for_external_read": True,
        "token_values_exposed": False,
        "commerce_external_writes_enabled": False,
        "live_execution_allowed": False,
    }
