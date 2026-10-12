from __future__ import annotations

from .release import CAPABILITIES
from .v60_proof import build_v60_acceptance, build_v60_proof


def build_v60_release_status() -> dict:
    proof = build_v60_proof()
    acceptance = build_v60_acceptance()
    capabilities = {
        **CAPABILITIES,
        "approval_intent_v55": True,
        "one_shot_contract_v56": True,
        "execution_receipt_v57": True,
        "recovery_plan_v58": True,
        "transition_gate_v59": True,
        "limited_live_gate_v60": True,
        "v60_proof": True,
        "v60_acceptance": True,
    }
    return {
        "release": "dropshipping-warashibe-v6.0-limited-live-gate",
        "status": "v6_gate_endpoint_reached" if proof["passed"] and acceptance["passed"] else "blocked",
        "proof_passed": proof["passed"],
        "acceptance_passed": acceptance["passed"],
        "capabilities": capabilities,
        "maturity_ceiling": "limited_live_gate_human_control",
        "human_gate_required": True,
        "automatic_execution_enabled": False,
        "external_writes_enabled": False,
        "live_execution_allowed": False,
    }
