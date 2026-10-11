from __future__ import annotations


def determine_next_action(
    *,
    credentials_ready: bool,
    persistence_ready: bool,
    observation_count: int,
    shadow_days: int,
    human_review_ready_count: int,
    min_observations: int = 20,
    min_shadow_days: int = 7,
) -> dict:
    if not credentials_ready:
        action = "configure_real_read_credentials"
        priority = 100
    elif not persistence_ready:
        action = "configure_supabase_server_secret"
        priority = 95
    elif int(observation_count) < int(min_observations):
        action = "collect_more_shadow_observations"
        priority = 90
    elif int(shadow_days) < int(min_shadow_days):
        action = "continue_shadow_days"
        priority = 85
    elif int(human_review_ready_count) > 0:
        action = "review_promotion_candidates"
        priority = 80
    else:
        action = "improve_candidate_discovery"
        priority = 70

    return {
        "next_action": action,
        "priority": priority,
        "automatic_live_action": False,
        "human_gate_required": action == "review_promotion_candidates",
    }
