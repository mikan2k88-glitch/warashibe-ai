"""Connect a read-only market provider to the canonical evidence ingestion boundary."""

from research_lab.live_market_evidence_ingestion import ingest_records
from research_lab.market_provider_contract import fetch_provider_records

PIPELINE_VERSION = "0.1"


def ingest_query(provider, query):
    """Fetch one explicit query and normalize its evidence without external writes."""
    provider_name, records = fetch_provider_records(provider, query)
    return ingest_records(provider_name, records)
