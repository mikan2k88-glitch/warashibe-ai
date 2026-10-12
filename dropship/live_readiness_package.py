from __future__ import annotations

from .live_preflight_audit import build_live_preflight_audit
from .v53_proof import build_v53_proof


def build_live_readiness_package(
    review: dict,
    *,
    existing_idempotency_keys: list[str] | None = None,
    limits: dict | None = None,
    kill_switch: bool | None = None,
    recovery: dict | None = None,
) -> dict:
    sandbox = build_v53_proof()
    audit = build_live_preflight_audit(
        review,
        existing_idempotency_keys=existing_idempotency_keys,
        limits=limits,
        kill_switch=kill_switch,
        recovery=recovery,
    )

    checks = {
        "sandbox_commerce_validated": sandbox["passed"] is True,
        "live_preflight_ready": audit["ready_for_human_gate"] is True,
        "human_gate_required": audit["human_gate_required"] is True,
        "live_execution_disabled": audit["live_execution_allowed"] is False,
    }
    ready = all(checks.values())

    return {
        "readiness_version": "5.4",
        "status": "ready_for_human_gate" if ready else "not_ready",
        "ready_for_human_gate": ready,
        "checks": checks,
        "audit": audit,
        "sandbox_proof_passed": sandbox["passed"],
        "allowed_next_action": "human_review_only" if ready else "resolve_readiness_gaps",
        "limited_live_execution_enabled": False,
        "commerce_write_enabled": False,
        "live_execution_allowed": False,
    }
