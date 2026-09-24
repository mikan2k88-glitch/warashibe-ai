"""Read-only snapshot across multiple market evidence providers."""

from dataclasses import dataclass
from datetime import datetime, timezone

from research_lab.provider_ingestion_pipeline import ingest_query

SNAPSHOT_VERSION = "0.1"


@dataclass(frozen=True)
class MultiProviderSnapshot:
    captured_at: str
    query: str
    provider_count: int
    raw_count: int
    rejected_count: int
    observations: tuple


def capture_market_snapshot(providers, query: str) -> MultiProviderSnapshot:
    """Query each injected read-only provider and combine normalized evidence."""
    if not query or not query.strip():
        raise ValueError("query is required")
    rows, raw_count, rejected_count = [], 0, 0
    providers = list(providers)
    for provider in providers:
        ingestion = ingest_query(provider, query)
        rows.extend(ingestion.accepted)
        raw_count += ingestion.raw_count
        rejected_count += ingestion.rejected_count
    return MultiProviderSnapshot(
        captured_at=datetime.now(timezone.utc).isoformat(),
        query=query.strip(),
        provider_count=len(providers),
        raw_count=raw_count,
        rejected_count=rejected_count,
        observations=tuple(rows),
    )
