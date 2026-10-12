from __future__ import annotations

from .release import CAPABILITIES
from .v62_proof import build_v62_acceptance, build_v62_proof


def build_v62_release_status() -> dict:
    proof = build_v62_proof()
    acceptance = build_v62_acceptance()
    capabilities = {
        **CAPABILITIES,
        "real_runtime_sources_v62": True,
        "actual_evidence_controller_v62": True,
        "persistent_evidence_reload_v62": True,
        "real_review_bridge_v62": True,
        "actual_evidence_workflow_v62": True,
    }
    return {
        "release": "dropshipping-warashibe-v6.2-actual-evidence-controller",
        "status": "actual_evidence_controller_endpoint_reached" if proof["passed"] and acceptance["passed"] else "blocked",
        "proof_passed": proof["passed"],
        "acceptance_passed": acceptance["passed"],
        "capabilities": capabilities,
        "maturity_ceiling": "actual_evidence_human_gate",
        "human_gate_required": True,
        "automatic_execution_enabled": False,
        "external_writes_enabled": False,
        "live_execution_allowed": False,
    }
