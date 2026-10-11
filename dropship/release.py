from __future__ import annotations

from .proof import build_acceptance, build_proof


CAPABILITIES = {
    "dll_concierge_registry_read": True,
    "supplier_provider_contract": True,
    "evidence_integrity": True,
    "economics": True,
    "policy_gate": True,
    "supplier_ranking": True,
    "single_item_selection": True,
    "working_capital_gate": True,
    "shadow_mode": True,
    "promotion_gate": True,
    "sandbox_commerce": True,
    "state_machine": True,
    "stop_loss": True,
    "duplicate_guard": True,
    "recovery_classifier": True,
    "audit_record": True,
    "burn_in_assessment": True,
    "live_readiness": True,
    "append_only_repository_contract": True,
    "supabase_research_schema": True,
    "hq_status": True,
    "human_gate_package": True,
    "freshness_gate": True,
    "provider_registry": True,
    "runtime_controller": True,
    "dll_degraded_mode": True,
    "dependency_health": True,
    "strategy_experiment": True,
    "walk_forward_validation": True,
    "champion_challenger_promotion": True,
    "human_gate_required": True,
    "live_commerce_enabled": False,
}


def build_release_status() -> dict:
    proof = build_proof()
    acceptance = build_acceptance()
    return {
        "release": "dropshipping-warashibe-v1.4-strategy-validation",
        "status": "research_endpoint_reached" if proof["passed"] and acceptance["passed"] else "blocked",
        "proof_passed": proof["passed"],
        "acceptance_passed": acceptance["passed"],
        "capabilities": CAPABILITIES,
        "maturity_ceiling": "ready_for_human_gate",
        "external_writes_enabled": False,
        "live_execution_allowed": False,
    }
