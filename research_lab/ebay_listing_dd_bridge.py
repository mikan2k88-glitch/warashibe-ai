"""Map one eBay listing to partial DD evidence without inventing sale facts."""

from datetime import datetime
from math import isfinite

from research_lab.real_market_schema import MarketObservation


def listing_observation_to_dd_input(observation: MarketObservation) -> dict:
    """Keep asking-price provenance and leave unavailable DD fields absent."""
    if (not isinstance(observation, MarketObservation)
            or observation.source != "ebay_browse"
            or not isinstance(observation.metadata, dict)
            or observation.metadata.get("asking_price_only") is not True
            or observation.currency != "JPY"
            or not isinstance(observation.external_id, str)
            or not observation.external_id.strip()
            or not isinstance(observation.purchase_price, (int, float))
            or isinstance(observation.purchase_price, bool)
            or not isfinite(observation.purchase_price)
            or observation.purchase_price <= 0):
        raise ValueError("validated eBay asking-price observation required")
    try:
        observed = datetime.fromisoformat(observation.observed_at)
    except (TypeError, ValueError):
        raise ValueError("dated eBay observation required") from None
    if observed.tzinfo is None or observed.utcoffset() is None:
        raise ValueError("timezone-aware eBay observation required")
    return {
        "item_id": observation.external_id,
        "purchase_price_jpy": observation.purchase_price,
        "price_evidence": "ebay_browse:" + observation.external_id,
        "evidence_metadata": {"price_evidence": {
            "source": "ebay_browse", "observed_at": observation.observed_at}},
        "metadata": {"asking_price_only": True},
    }
