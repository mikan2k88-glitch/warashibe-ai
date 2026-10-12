from __future__ import annotations

from .observations import summarize_observations
from .pipeline import run_dropship_decision_pipeline


def run_research_cycle(offers: list[dict], historical_observations: list[dict] | None = None) -> dict:
    history = list(historical_observations or [])
    history.extend(dict(row) for row in offers)
    observation_summary = summarize_observations(history)
    decision = run_dropship_decision_pipeline(offers)

    return {
        "status": "completed",
        "mode": "research",
        "observation_summary": observation_summary,
        "decision": decision,
        "selected_product_key": decision.get("selected_product_key"),
        "external_writes": False,
        "real_listing": False,
        "real_order": False,
        "live_execution_allowed": False,
    }
