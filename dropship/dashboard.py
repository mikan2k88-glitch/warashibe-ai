from __future__ import annotations

from .maturity import determine_maturity


def build_dashboard_summary(state: dict) -> dict:
    maturity = determine_maturity(state)
    return {
        "service": "warashibe-dropshipping",
        "version": state.get("version"),
        "maturity": maturity,
        "candidate_count": int(state.get("candidate_count") or 0),
        "eligible_count": int(state.get("eligible_count") or 0),
        "shadow_observations": int(state.get("shadow_observations") or 0),
        "shadow_days": int(state.get("shadow_days") or 0),
        "sandbox_cycles": int(state.get("sandbox_cycles") or 0),
        "estimated_net_profit": float(state.get("estimated_net_profit") or 0),
        "live_execution_allowed": False,
        "external_writes_enabled": False,
        "next_focus": (
            "human_gate_review"
            if maturity["stage"] == "live_readiness"
            else "collect_evidence"
        ),
    }
