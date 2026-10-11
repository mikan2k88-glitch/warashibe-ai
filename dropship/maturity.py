from __future__ import annotations


STAGES = (
    "research",
    "shadow",
    "sandbox",
    "live_readiness",
    "human_gate",
    "limited_live",
    "burn_in",
    "controlled_automation",
)


def determine_maturity(evidence: dict) -> dict:
    stage = "research"
    if int(evidence.get("shadow_observations") or 0) > 0:
        stage = "shadow"
    if int(evidence.get("sandbox_cycles") or 0) > 0:
        stage = "sandbox"
    if evidence.get("ready_for_human_gate") is True:
        stage = "live_readiness"

    return {
        "stage": stage,
        "stage_index": STAGES.index(stage),
        "allowed_actions": {
            "research_reads": True,
            "shadow": stage in {"shadow", "sandbox", "live_readiness"},
            "sandbox": stage in {"sandbox", "live_readiness"},
            "live_listing": False,
            "live_supplier_order": False,
            "live_payment": False,
        },
        "human_gate_required_for_next_live_stage": True,
    }
