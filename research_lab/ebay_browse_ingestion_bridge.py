"""Bridge validated eBay Browse search payloads into canonical market evidence.

Browse search prices remain asking-price evidence only.  This bridge performs no
network calls, purchases, listings, payments, or sale-outcome persistence.
"""

from dataclasses import dataclass

from research_lab.ebay_browse_adapter import browse_search_to_records
from research_lab.live_market_evidence_ingestion import IngestionResult, ingest_records

BRIDGE_VERSION = "0.1"


@dataclass(frozen=True)
class EbayBrowseIngestionResult:
    ingestion: IngestionResult
    mapping_rejected: tuple[dict, ...]

    @property
    def accepted(self):
        return self.ingestion.accepted

    @property
    def accepted_count(self):
        return self.ingestion.accepted_count

    @property
    def rejected_count(self):
        return len(self.mapping_rejected) + self.ingestion.rejected_count


def ingest_browse_search_payload(payload, *, observed_at=None):
    """Map one already-fetched Browse payload and ingest only validated evidence."""
    records, mapping_rejected = browse_search_to_records(
        payload, observed_at=observed_at
    )
    ingestion = ingest_records("ebay_browse", records)
    return EbayBrowseIngestionResult(
        ingestion=ingestion,
        mapping_rejected=tuple(mapping_rejected),
    )
