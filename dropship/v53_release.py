from __future__ import annotations

from .release import CAPABILITIES
from .v53_proof import build_v53_acceptance, build_v53_proof


def build_v53_release_status() -> dict:
    proof = build_v53_proof()
    acceptance = build_v53_acceptance()
    capabilities = {
        **CAPABILITIES,
        "listing_preview_v53": True,
        "sandbox_customer_order_v53": True,
        "sandbox_supplier_order_v53": True,
        "sandbox_fulfillment_v53": True,
        "sandbox_settlement_v53": True,
        "sandbox_failure_scenarios_v53": True,
        "sandbox_outcome_v53": True,
    }
    return {
        "release": "dropshipping-warashibe-v5.3-sandbox-commerce-validation",
        "status": "sandbox_commerce_endpoint_reached" if proof["passed"] and acceptance["passed"] else "blocked",
        "proof_passed": proof["passed"],
        "acceptance_passed": acceptance["passed"],
        "capabilities": capabilities,
        "maturity_ceiling": "sandbox_commerce_validated",
        "commerce_external_writes_enabled": False,
        "real_listing_enabled": False,
        "real_supplier_order_enabled": False,
        "real_payment_enabled": False,
        "live_execution_allowed": False,
    }
