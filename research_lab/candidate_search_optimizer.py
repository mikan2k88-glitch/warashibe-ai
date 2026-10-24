"""P2 Candidate Search v2.6: adaptive search-priority optimizer.

This module optimizes *what to investigate next*. It does not modify production
policy, execute commerce, or weaken any evidence/Human Gate.

The objective is capital velocity with evidence quality:
    expected profit x sale probability / expected hold days
then bounded quality multipliers for evidence, source quality, cost certainty,
and acquisition headroom.

Failure history changes the next search allocation. This is intentionally
rule-based until enough real outcomes exist for statistical/ML optimization.
"""

from collections import Counter
from dataclasses import dataclass
from math import isfinite
from typing import Any, Iterable

OPTIMIZER_VERSION = "2.6"

FAILURE_REASONS = {
    "shipping_loss",
    "insufficient_margin",
    "low_liquidity",
    "condition_mismatch",
    "edition_mismatch",
    "unstable_price",
    "stale_evidence",
    "source_unavailable",
    "authenticity_risk",
    "over_capital",
    "sold_evidence_insufficient",
    "other",
}


def _number(value: Any, name: str, *, minimum: float = 0.0) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric")
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be numeric") from None
    if not isfinite(parsed) or parsed < minimum:
        raise ValueError(f"{name} must be finite and >= {minimum}")
    return parsed


def _ratio(value: Any, name: str) -> float:
    parsed = _number(value, name)
    if parsed > 1:
        raise ValueError(f"{name} must be between 0 and 1")
    return parsed


def _score_100(value: Any, name: str) -> float:
    parsed = _number(value, name)
    if parsed > 100:
        raise ValueError(f"{name} must be between 0 and 100")
    return parsed


@dataclass(frozen=True)
class SearchCandidate:
    identity_key: str
    category: str
    expected_net_profit_jpy: float
    sale_probability: float
    expected_hold_days: float
    evidence_confidence: float
    source_quality_score: float
    cost_certainty_score: float
    total_acquisition_jpy: float
    max_total_acquisition_jpy: float
    sold_comp_count: int
    source_count: int


def normalize_candidate(raw: dict[str, Any]) -> SearchCandidate:
    if not isinstance(raw, dict):
        raise ValueError("candidate must be a dictionary")
    identity = str(raw.get("identity_key") or "").strip()
    category = str(raw.get("category") or "").strip()
    if not identity:
        raise ValueError("identity_key is required")
    if not category:
        raise ValueError("category is required")

    sold = raw.get("sold_comp_count", 0)
    sources = raw.get("source_count", 0)
    if isinstance(sold, bool) or not isinstance(sold, int) or sold < 0:
        raise ValueError("sold_comp_count must be a non-negative integer")
    if isinstance(sources, bool) or not isinstance(sources, int) or sources < 0:
        raise ValueError("source_count must be a non-negative integer")

    return SearchCandidate(
        identity_key=identity,
        category=category,
        expected_net_profit_jpy=_number(
            raw.get("expected_net_profit_jpy"), "expected_net_profit_jpy"
        ),
        sale_probability=_ratio(raw.get("sale_probability"), "sale_probability"),
        expected_hold_days=_number(
            raw.get("expected_hold_days"), "expected_hold_days", minimum=0.01
        ),
        evidence_confidence=_score_100(
            raw.get("evidence_confidence"), "evidence_confidence"
        ),
        source_quality_score=_score_100(
            raw.get("source_quality_score"), "source_quality_score"
        ),
        cost_certainty_score=_score_100(
            raw.get("cost_certainty_score"), "cost_certainty_score"
        ),
        total_acquisition_jpy=_number(
            raw.get("total_acquisition_jpy"), "total_acquisition_jpy"
        ),
        max_total_acquisition_jpy=_number(
            raw.get("max_total_acquisition_jpy"), "max_total_acquisition_jpy"
        ),
        sold_comp_count=sold,
        source_count=sources,
    )


def _headroom_ratio(candidate: SearchCandidate) -> float:
    ceiling = candidate.max_total_acquisition_jpy
    if ceiling <= 0:
        return 0.0
    return max(0.0, min(1.0, (ceiling - candidate.total_acquisition_jpy) / ceiling))


def score_search_candidate(candidate: SearchCandidate | dict[str, Any]) -> dict[str, Any]:
    """Score investigation priority; this is not a purchase/selection approval."""
    item = candidate if isinstance(candidate, SearchCandidate) else normalize_candidate(candidate)

    capital_velocity = (
        item.expected_net_profit_jpy
        * item.sale_probability
        / item.expected_hold_days
    )
    # Saturating velocity score: JPY100 expected profit/day already scores 100.
    velocity_score = min(100.0, capital_velocity)

    evidence_score = item.evidence_confidence
    source_score = item.source_quality_score
    cost_score = item.cost_certainty_score
    headroom_score = _headroom_ratio(item) * 100
    sold_depth_score = min(100.0, item.sold_comp_count * 25.0)
    source_diversity_score = min(100.0, item.source_count * 25.0)

    total = (
        velocity_score * 0.35
        + evidence_score * 0.20
        + source_score * 0.15
        + cost_score * 0.10
        + headroom_score * 0.10
        + sold_depth_score * 0.05
        + source_diversity_score * 0.05
    )

    # Hard research penalties. These do not replace formal gates; they only
    # prevent wasting search budget on obviously immature candidates.
    penalties = []
    if item.sold_comp_count < 2:
        total -= 25
        penalties.append("sold_evidence_insufficient")
    if item.source_count < 2:
        total -= 10
        penalties.append("source_diversity_low")
    if item.total_acquisition_jpy > item.max_total_acquisition_jpy:
        total -= 40
        penalties.append("over_acquisition_ceiling")
    if item.cost_certainty_score < 60:
        total -= 15
        penalties.append("cost_certainty_low")

    score = round(max(0.0, min(100.0, total)), 2)
    return {
        "version": OPTIMIZER_VERSION,
        "identity_key": item.identity_key,
        "category": item.category,
        "priority_score": score,
        "capital_velocity_jpy_per_day": round(capital_velocity, 2),
        "score_components": {
            "velocity": round(velocity_score, 2),
            "evidence": round(evidence_score, 2),
            "source_quality": round(source_score, 2),
            "cost_certainty": round(cost_score, 2),
            "acquisition_headroom": round(headroom_score, 2),
            "sold_depth": round(sold_depth_score, 2),
            "source_diversity": round(source_diversity_score, 2),
        },
        "penalties": penalties,
        "human_gate_required": True,
        "external_execution_authorized": False,
        "purchase_authorized": False,
    }


def rank_search_candidates(candidates: Iterable[SearchCandidate | dict[str, Any]]) -> list[dict[str, Any]]:
    scored = [score_search_candidate(candidate) for candidate in candidates]
    scored.sort(
        key=lambda row: (
            -row["priority_score"],
            -row["capital_velocity_jpy_per_day"],
            row["identity_key"],
        )
    )
    for index, row in enumerate(scored, start=1):
        row["search_rank"] = index
    return scored


def optimize_next_search_strategy(
    rejection_reasons: Iterable[str],
    *,
    recent_category_results: dict[str, dict[str, int]] | None = None,
) -> dict[str, Any]:
    """Turn rejection history into bounded next-run search allocation advice."""
    reasons = [str(reason) for reason in rejection_reasons]
    unknown = [reason for reason in reasons if reason not in FAILURE_REASONS]
    if unknown:
        raise ValueError(f"unsupported rejection reasons: {sorted(set(unknown))}")

    counts = Counter(reasons)
    dominant = [name for name, _ in counts.most_common(3)]
    actions = []

    if counts["sold_evidence_insufficient"]:
        actions.append("increase_sold_seed_search_before_source_search")
    if counts["insufficient_margin"] or counts["over_capital"]:
        actions.append("shift_to_lower_acquisition_or_higher_resale_band")
    if counts["shipping_loss"]:
        actions.append("prioritize_free_or_known_shipping_and_small_light_items")
    if counts["low_liquidity"]:
        actions.append("increase_recent_sold_frequency_requirement")
    if counts["edition_mismatch"] or counts["condition_mismatch"]:
        actions.append("move_identity_and_condition_checks_earlier")
    if counts["stale_evidence"] or counts["source_unavailable"]:
        actions.append("prioritize_fresh_live_stock_sources")
    if counts["unstable_price"]:
        actions.append("prefer_lower_price_dispersion_candidates")
    if counts["authenticity_risk"]:
        actions.append("deprioritize_authenticity_sensitive_categories")
    if not actions:
        actions.append("keep_current_search_mix")

    category_weights = {}
    results = recent_category_results or {}
    if not isinstance(results, dict):
        raise ValueError("recent_category_results must be a mapping")
    raw_weights = {}
    for category, metrics in results.items():
        if not isinstance(metrics, dict):
            raise ValueError("category metrics must be mappings")
        seeds = metrics.get("seed_pass", 0)
        eligible = metrics.get("selection_eligible", 0)
        near = metrics.get("near_p3_shadow", 0)
        searched = metrics.get("searched", 0)
        for value in (seeds, eligible, near, searched):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError("category metrics must be non-negative integers")
        # Laplace-style smoothing prevents zero-history categories disappearing.
        effectiveness = (1 + 4 * eligible + 2 * near + seeds) / (4 + searched)
        raw_weights[str(category)] = effectiveness

    if raw_weights:
        total = sum(raw_weights.values())
        category_weights = {
            category: round(weight / total, 4)
            for category, weight in raw_weights.items()
        }
        # Exploration floor and concentration cap: preserve discovery diversity.
        if len(category_weights) > 1:
            capped = {
                category: min(0.70, max(0.05, weight))
                for category, weight in category_weights.items()
            }
            cap_total = sum(capped.values())
            category_weights = {
                category: round(weight / cap_total, 4)
                for category, weight in capped.items()
            }

    return {
        "version": OPTIMIZER_VERSION,
        "status": "search_strategy_optimized",
        "rejection_counts": dict(counts),
        "dominant_rejection_reasons": dominant,
        "next_run_actions": list(dict.fromkeys(actions)),
        "category_weights": category_weights,
        "objective": "maximize_capital_velocity_with_evidence_quality",
        "production_rule_changed": False,
        "requires_shadow_validation": True,
        "human_gate_required": True,
        "external_execution_authorized": False,
        "purchase_authorized": False,
    }


__all__ = [
    "FAILURE_REASONS",
    "SearchCandidate",
    "normalize_candidate",
    "score_search_candidate",
    "rank_search_candidates",
    "optimize_next_search_strategy",
]
