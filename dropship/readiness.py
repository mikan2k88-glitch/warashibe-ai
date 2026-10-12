from __future__ import annotations


def assess_live_readiness(evidence: dict) -> dict:
    checks = {
        "shadow_observations_minimum": int(evidence.get("shadow_observations") or 0) >= 20,
        "shadow_days_minimum": int(evidence.get("shadow_days") or 0) >= 30,
        "sandbox_cycles_minimum": int(evidence.get("sandbox_cycles") or 0) >= 10,
        "evidence_integrity_passed": evidence.get("evidence_integrity_passed") is True,
        "promotion_gate_passed": evidence.get("promotion_gate_passed") is True,
        "duplicate_order_guard": evidence.get("duplicate_order_guard") is True,
        "kill_switch_ready": evidence.get("kill_switch_ready") is True,
        "audit_log_ready": evidence.get("audit_log_ready") is True,
        "external_writes_still_disabled": evidence.get("external_writes_enabled") is False,
    }
    ready = all(checks.values())
    return {
        "status": "ready_for_human_gate" if ready else "blocked",
        "checks": checks,
        "research_ready_for_human_gate": ready,
        "human_gate_required": True,
        "live_execution_allowed": False,
        "next_stage": "human_gate" if ready else "shadow_sandbox",
    }
