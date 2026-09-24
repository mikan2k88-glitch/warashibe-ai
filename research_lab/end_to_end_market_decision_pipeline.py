"""End-to-end read-only market evidence to decision pipeline."""

from dataclasses import dataclass

from research_lab.conflict_aware_evidence_grouping import estimate_conflict_aware
from research_lab.provider_ingestion_pipeline import ingest_query
from research_lab.quality_gated_candidate_pipeline import evaluate_quality_gated_estimates

END_TO_END_VERSION = "0.1"


@dataclass(frozen=True)
class MarketDecisionRun:
    provider: str
    query: str
    raw_count: int
    normalized_count: int
    normalization_rejected: int
    estimate_count: int
    decision: dict


def run_market_decision(provider, query: str, current_capital: float, **gate_kwargs) -> MarketDecisionRun:
    """Fetch one explicit read-only query and produce a quality-gated decision."""
    ingestion = ingest_query(provider, query)
    estimates = estimate_conflict_aware(ingestion.accepted)
    decision = evaluate_quality_gated_estimates(estimates, current_capital, **gate_kwargs)
    decision["end_to_end_version"] = END_TO_END_VERSION
    return MarketDecisionRun(
        provider=ingestion.provider,
        query=query.strip(),
        raw_count=ingestion.raw_count,
        normalized_count=ingestion.accepted_count,
        normalization_rejected=ingestion.rejected_count,
        estimate_count=len(estimates),
        decision=decision,
    )
