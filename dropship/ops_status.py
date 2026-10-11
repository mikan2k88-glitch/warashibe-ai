from __future__ import annotations

from .token_readiness import assess_token_readiness
from .next_action import determine_next_action
from .ops_summary import summarize_operations
from .persistence_health import assess_persistence_environment



def build_ops_status(
    observations: list[dict],
    runs: list[dict],
    *,
    promotion_reviews: list[dict] | None = None,
) -> dict:
    summary = summarize_operations(
        observations,
        runs,
        promotion_reviews=promotion_reviews,
    )
    credentials = assess_token_readiness()
    persistence = assess_persistence_environment()

    max_shadow_days = max(
        [int(row.get("observation_days") or 0) for row in summary["products"]] or [0]
    )
    next_action = determine_next_action(
        credentials_ready=credentials["all_ready"],
        persistence_ready=persistence["status"] == "ready",
        observation_count=summary["observation_count"],
        shadow_days=max_shadow_days,
        human_review_ready_count=summary["human_review_ready_count"],
    )

    return {
        "status": "ops_status_ready",
        "mode": "research_shadow",
        "credentials": credentials,
        "persistence": persistence,
        "summary": summary,
        "next_action": next_action,
        "commerce_external_writes": False,
        "live_execution_allowed": False,
    }
