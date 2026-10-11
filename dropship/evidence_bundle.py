from __future__ import annotations

from .readiness import assess_live_readiness


def build_readiness_evidence(
    *,
    shadow_observations: int,
    shadow_days: int,
    sandbox_cycles: int,
    evidence_integrity_passed: bool,
    promotion_gate_passed: bool,
    duplicate_order_guard: bool = True,
    kill_switch_ready: bool = True,
    audit_log_ready: bool = True,
) -> dict:
    evidence = {
        "shadow_observations": int(shadow_observations),
        "shadow_days": int(shadow_days),
        "sandbox_cycles": int(sandbox_cycles),
        "evidence_integrity_passed": bool(evidence_integrity_passed),
        "promotion_gate_passed": bool(promotion_gate_passed),
        "duplicate_order_guard": bool(duplicate_order_guard),
        "kill_switch_ready": bool(kill_switch_ready),
        "audit_log_ready": bool(audit_log_ready),
        "external_writes_enabled": False,
    }
    return {
        "evidence": evidence,
        "readiness": assess_live_readiness(evidence),
        "live_execution_allowed": False,
    }
