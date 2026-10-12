from __future__ import annotations

from .freshness import assess_freshness
from .hq import build_hq_status
from .research_cycle import run_research_cycle


def run_runtime_controller(
    offers: list[dict],
    *,
    historical_observations: list[dict] | None = None,
    max_age_hours: float = 24.0,
) -> dict:
    freshness_rows = []
    fresh_offers = []
    stale_offers = []

    for offer in offers:
        check = assess_freshness(
            offer.get("observed_at"),
            max_age_hours=max_age_hours,
        )
        row = {
            "product_key": offer.get("product_key"),
            "freshness": check,
        }
        freshness_rows.append(row)
        if check["fresh"]:
            fresh_offers.append(offer)
        else:
            stale_offers.append(offer)

    if not fresh_offers:
        hq = build_hq_status({
            "eligible_count": 0,
            "shadow_days": 0,
            "sandbox_cycles": 0,
            "evidence_integrity_passed": False,
        })
        return {
            "status": "blocked",
            "reason": "no_fresh_offers",
            "freshness": freshness_rows,
            "fresh_offer_count": 0,
            "stale_offer_count": len(stale_offers),
            "hq": hq,
            "external_writes": False,
            "live_execution_allowed": False,
        }

    research = run_research_cycle(
        fresh_offers,
        historical_observations=historical_observations,
    )
    decision = research.get("decision") or {}
    hq = build_hq_status({
        "eligible_count": (decision.get("ranking") or {}).get("eligible_count", 0),
        "shadow_days": (research.get("observation_summary") or {}).get("products", [{}])[0].get("observation_days", 0)
        if (research.get("observation_summary") or {}).get("products")
        else 0,
        "sandbox_cycles": 1 if decision.get("status") == "completed" else 0,
        "evidence_integrity_passed": decision.get("status") in {"completed", "collecting"},
    })
    return {
        "status": "completed",
        "freshness": freshness_rows,
        "fresh_offer_count": len(fresh_offers),
        "stale_offer_count": len(stale_offers),
        "research": research,
        "hq": hq,
        "external_writes": False,
        "live_execution_allowed": False,
    }
