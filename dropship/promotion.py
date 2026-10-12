from __future__ import annotations


def assess_promotion(shadow_result: dict) -> dict:
    checks = {
        "shadow_mode": shadow_result.get("mode") == "shadow",
        "evidence_integrity_passed": shadow_result.get("evidence_integrity_passed") is True,
        "policy_allowed": (shadow_result.get("policy") or {}).get("allowed") is True,
        "positive_expected_profit": (shadow_result.get("economics") or {}).get("net_profit", 0) > 0,
        "no_external_writes": shadow_result.get("external_writes") is False,
    }
    ready = all(checks.values())
    return {
        "status": "promotion_ready" if ready else "research_usable_not_promotion_ready",
        "checks": checks,
        "promotion_ready": ready,
        "next_stage": "sandbox" if ready else "shadow",
        "live_execution_allowed": False,
        "human_gate_required_for_live": True,
    }
