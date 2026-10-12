from __future__ import annotations

from .release import CAPABILITIES
from .v65_proof import build_v65_acceptance, build_v65_proof


def build_v65_release_status() -> dict:
    proof = build_v65_proof()
    acceptance = build_v65_acceptance()
    return {
        "release": "dropshipping-warashibe-v6.5-cost-evidence-acquisition",
        "status": (
            "cost_evidence_acquisition_endpoint_reached"
            if proof["passed"] and acceptance["passed"]
            else "blocked"
        ),
        "proof_passed": proof["passed"],
        "acceptance_passed": acceptance["passed"],
        "capabilities": {
            **CAPABILITIES,
            "cj_freight_read_v65": True,
            "shipping_cost_evidence_v65": True,
            "actual_evidence_controller_v65": True,
        },
        "maturity_ceiling": "cost_evidence_acquisition_human_gate",
        "human_gate_required": True,
        "automatic_execution_enabled": False,
        "external_writes_enabled": False,
        "live_execution_allowed": False,
    }
