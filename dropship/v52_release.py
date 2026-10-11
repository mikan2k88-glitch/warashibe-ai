from __future__ import annotations

from .release import CAPABILITIES
from .v52_proof import build_v52_acceptance, build_v52_proof


def build_v52_release_status() -> dict:
    proof = build_v52_proof()
    acceptance = build_v52_acceptance()
    capabilities = {
        **CAPABILITIES,
        "provider_diagnostics_v42": True,
        "real_shadow_collection_v43": True,
        "discovery_planner_v44": True,
        "market_confidence_v45": True,
        "real_product_ranking_v50": True,
        "long_shadow_evidence_v51": True,
        "promotion_review_v52": True,
        "promotion_queue_v52": True,
    }
    return {
        "release": "dropshipping-warashibe-v5.2-promotion-review",
        "status": "promotion_review_endpoint_reached" if proof["passed"] and acceptance["passed"] else "blocked",
        "proof_passed": proof["passed"],
        "acceptance_passed": acceptance["passed"],
        "capabilities": capabilities,
        "maturity_ceiling": "promotion_review_human_gate",
        "commerce_external_writes_enabled": False,
        "automatic_promotion_enabled": False,
        "live_execution_allowed": False,
    }
