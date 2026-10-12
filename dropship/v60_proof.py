from __future__ import annotations

from .human_gate import verify_human_approval
from .limited_live_gate_v60 import build_v60_gate
from .v52_proof import build_v52_proof


def build_v60_proof() -> dict:
    review = build_v52_proof()["review"]
    gate = build_v60_gate(review)
    approval = verify_human_approval("8888")

    checks = {
        "gate_passed": gate["passed"] is True,
        "human_gate_required": gate["human_gate_required"] is True,
        "approval_verified": approval["approved"] is True,
        "approval_does_not_execute": approval["live_execution_allowed"] is False,
        "one_shot_contract": gate["contract"]["single_use"] is True,
        "receipt_not_executed": gate["receipt"]["result"] == "not_executed",
        "automatic_execution_disabled": gate["automatic_execution"] is False,
        "external_write_disabled": gate["external_write_enabled"] is False,
        "live_execution_disabled": gate["live_execution_allowed"] is False,
    }

    return {
        "proof_version": "6.0",
        "passed": all(checks.values()),
        "checks": checks,
        "gate": gate,
        "approval": approval,
        "maturity_ceiling": "limited_live_gate_human_control",
        "live_execution_allowed": False,
    }


def build_v60_acceptance() -> dict:
    proof = build_v60_proof()
    checks = {
        "proof_passed": proof["passed"],
        "gate_ready": proof["gate"]["status"] == "limited_live_gate_ready",
        "human_control_preserved": proof["gate"]["human_gate_required"] is True,
        "no_automatic_execution": proof["gate"]["automatic_execution"] is False,
        "no_external_write": proof["gate"]["external_write_enabled"] is False,
        "live_execution_disabled": proof["live_execution_allowed"] is False,
    }
    return {
        "acceptance_version": "6.0",
        "passed": all(checks.values()),
        "checks": checks,
        "endpoint": "limited_live_gate_human_control",
        "next_phase": "real_provider_evidence_then_explicit_human_decision",
        "live_execution_allowed": False,
    }
