"""Bridge validated eBay Browse search payloads into canonical market evidence.

Browse search prices remain asking-price evidence only.  This bridge performs no
network calls, purchases, listings, payments, or sale-outcome persistence.
"""

from dataclasses import dataclass
import os

from research_lab.ebay_browse_adapter import browse_search_to_records
from research_lab.ebay_browse_transport import fetch_search_payload
from research_lab.ebay_listing_dd_bridge import listing_observation_to_dd_input
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


def build_dd_input_batch(result: EbayBrowseIngestionResult) -> dict:
    """Convert accepted listings separately; one unsuitable row cannot promote others."""
    if not isinstance(result, EbayBrowseIngestionResult):
        raise ValueError("eBay ingestion result required")
    inputs, rejected = [], []
    for observation in result.accepted:
        try:
            inputs.append(listing_observation_to_dd_input(observation))
        except ValueError:
            rejected.append({"item_id": observation.external_id,
                             "reason": "dd_conversion_rejected"})
    return {"dd_inputs": tuple(inputs), "rejected": tuple(rejected),
            "external_action_authorized": False}


def fetch_and_ingest_browse_search(
    query,
    access_token,
    *,
    marketplace_id="EBAY_US",
    limit=20,
    timeout=10,
    fetch_payload=fetch_search_payload,
    observed_at=None,
):
    """Fetch one read-only Browse search and ingest validated market evidence.

    The injected fetcher keeps tests deterministic. The default transport is
    restricted to eBay Browse GET item_summary/search and exposes no commerce
    operation.
    """
    payload = fetch_payload(
        query,
        access_token,
        marketplace_id=marketplace_id,
        limit=limit,
        timeout=timeout,
    )
    return ingest_browse_search_payload(payload, observed_at=observed_at)


def fetch_and_ingest_browse_from_environment(
    query,
    *,
    environ=None,
    marketplace_id="EBAY_US",
    limit=20,
    timeout=10,
    fetch_payload=fetch_search_payload,
    observed_at=None,
):
    """Read the eBay token from environment and run one read-only ingestion.

    Missing credentials fail closed. The token is passed only to the transport
    call and is never included in the returned ingestion result.
    """
    env = os.environ if environ is None else environ
    token = str(env.get("EBAY_BROWSE_ACCESS_TOKEN") or "").strip()
    if not token:
        raise RuntimeError("eBay Browse access token is not configured")
    return fetch_and_ingest_browse_search(
        query,
        token,
        marketplace_id=marketplace_id,
        limit=limit,
        timeout=timeout,
        fetch_payload=fetch_payload,
        observed_at=observed_at,
    )
