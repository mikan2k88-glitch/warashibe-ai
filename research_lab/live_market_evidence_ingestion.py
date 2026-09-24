"""Read-only ingestion boundary for live market evidence.

Providers return raw listing/evidence dictionaries.  This module validates and
normalizes them without buying, listing, paying, or inventing missing market
facts.  Real provider credentials and HTTP clients stay outside this layer.
"""

from dataclasses import dataclass
from typing import Callable, Iterable

from research_lab.real_market_schema import MarketObservation
from research_lab.real_market_source_adapter import normalize_source_batch

INGESTION_VERSION = "0.1"


@dataclass(frozen=True)
class IngestionResult:
    provider: str
    accepted: tuple[MarketObservation, ...]
    rejected: tuple[dict, ...]
    raw_count: int

    @property
    def accepted_count(self):
        return len(self.accepted)

    @property
    def rejected_count(self):
        return len(self.rejected)


def ingest_records(provider: str, records: Iterable[dict]) -> IngestionResult:
    """Normalize an already-fetched read-only batch."""
    rows = list(records)
    accepted, rejected = normalize_source_batch(rows)
    return IngestionResult(
        provider=str(provider).strip() or "unknown",
        accepted=tuple(accepted),
        rejected=tuple(rejected),
        raw_count=len(rows),
    )


def ingest_provider(provider: str, fetch: Callable[[], Iterable[dict]]) -> IngestionResult:
    """Fetch through an injected read-only provider and normalize its batch.

    The provider function owns network/auth concerns.  Keeping it injected makes
    CI deterministic and prevents the research runner from requiring secrets.
    """
    return ingest_records(provider, fetch())
