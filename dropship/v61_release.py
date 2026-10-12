from __future__ import annotations

from .release import CAPABILITIES
from .v61_proof import build_v61_acceptance, build_v61_proof


def build_v61_release_status() -> dict:
    proof = build_v61_proof()
    acceptance = build_v61_acceptance()
    capabilities = {
        **CAPABILITIES,
        "real_evidence_qualification_v61": True,
        "fixture_rejection_v61": True,
        "persistent_history_required_v61": True,
        "provider_handshake_required_v61": True,
        "v61_real_gate": True,
    }
    return {
        "release": "dropshipping-warashibe-v6.1-real-evidence-gate",
        "status": "real_evidence_gate_endpoint_reached" if proof["passed"] and acceptance["passed"] else "blocked",
        "proof_passed": proof["passed"],
        "acceptance_passed": acceptance["passed"],
        "capabilities": capabilities,
        "maturity_ceiling": "real_evidence_human_gate",
        "human_gate_required": True,
        "automatic_execution_enabled": False,
        "external_writes_enabled": False,
        "live_execution_allowed": False,
    }
