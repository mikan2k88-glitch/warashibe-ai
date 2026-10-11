from __future__ import annotations

from .capital import assess_working_capital
from .economics import evaluate_dropship_economics
from .freshness import assess_freshness
from .platform_adapter import SandboxSalesChannelAdapter
from .policy_profile import evaluate_policy_profile


def run_preflight(
    candidate: dict,
    *,
    available_capital: float,
    max_age_hours: float = 24.0,
    policy_profile: dict | None = None,
) -> dict:
    economics = evaluate_dropship_economics(candidate)
    capital = assess_working_capital(economics, available_capital)
    freshness = assess_freshness(
        candidate.get("observed_at"),
        max_age_hours=max_age_hours,
    )
    policy = evaluate_policy_profile(candidate, economics, policy_profile)
    preview = SandboxSalesChannelAdapter().build_listing_preview(candidate)

    checks = {
        "economics_profitable": economics["profitable"],
        "capital_allowed": capital["allowed"],
        "fresh": freshness["fresh"],
        "policy_allowed": policy["allowed"],
        "listing_preview_only": preview["external_write"] is False,
    }
    passed = all(checks.values())
    return {
        "status": "preflight_passed" if passed else "preflight_blocked",
        "passed": passed,
        "checks": checks,
        "economics": economics,
        "capital": capital,
        "freshness": freshness,
        "policy": policy,
        "listing_preview": preview,
        "human_gate_required_for_live": True,
        "live_execution_allowed": False,
    }
