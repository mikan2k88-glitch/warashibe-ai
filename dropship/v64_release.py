from __future__ import annotations

from .release import CAPABILITIES
from .v64_proof import build_v64_acceptance, build_v64_proof


def build_v64_release_status() -> dict:
    proof = build_v64_proof()
    acceptance = build_v64_acceptance()
    capabilities = {
        **CAPABILITIES,
        "cost_completeness_gate_v64": True,
        "terms_evidence_gate_v64": True,
        "cj_unknown_cost_markers_v64": True,
        "actual_evidence_controller_v64": True,
    }
    return {
        "release": "dropshipping-warashibe-v6.4-cost-completeness",
        "status": (
            "cost_completeness_endpoint_reached"
            if proof["passed"] and acceptance["passed"]
            else "blocked"
        ),
        "proof_passed": proof["passed"],
        "acceptance_passed": acceptance["passed"],
        "capabilities": capabilities,
        "maturity_ceiling": "cost_and_terms_evidence_human_gate",
        "human_gate_required": True,
        "automatic_execution_enabled": False,
        "external_writes_enabled": False,
        "live_execution_allowed": False,
    }
