from __future__ import annotations

from .candidate_builder import build_latest_candidates
from .data_quality import filter_quality
from .dedupe import deduplicate_observations
from .provider_normalizer import normalize_provider_row
from .runtime_controller import run_runtime_controller


def run_collection_pipeline(
    rows: list[dict],
    *,
    provider_name: str,
    historical_observations: list[dict] | None = None,
    max_age_hours: float = 24.0,
    min_quality_score: float = 0.8,
) -> dict:
    normalized = [
        normalize_provider_row(row, provider_name=provider_name)
        for row in rows
        if isinstance(row, dict)
    ]
    dedupe = deduplicate_observations(normalized)
    quality = filter_quality(dedupe["unique"], min_score=min_quality_score)
    candidates = build_latest_candidates(quality["passed"])
    runtime = run_runtime_controller(
        candidates,
        historical_observations=historical_observations,
        max_age_hours=max_age_hours,
    )
    return {
        "status": "completed" if candidates else "blocked",
        "provider_name": provider_name,
        "input_count": len(rows),
        "normalized_count": len(normalized),
        "duplicate_count": dedupe["duplicate_count"],
        "quality_passed_count": quality["passed_count"],
        "quality_blocked_count": quality["blocked_count"],
        "candidate_count": len(candidates),
        "candidates": candidates,
        "runtime": runtime,
        "external_writes": False,
        "live_execution_allowed": False,
    }
