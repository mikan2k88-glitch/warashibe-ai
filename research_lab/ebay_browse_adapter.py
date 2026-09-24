"""Pure read-only adapter from eBay Browse API search payloads to raw market evidence.

Authentication and HTTP transport stay outside this module. The caller supplies
an already-fetched Browse API JSON payload, so credentials never enter the
research pipeline and this adapter cannot buy, list, pay, or mutate eBay data.
"""

from datetime import datetime, timezone

EBAY_BROWSE_ADAPTER_VERSION = "0.1"


def _money(value):
    if not isinstance(value, dict) or value.get("value") in (None, ""):
        raise ValueError("listing price is required")
    return float(value["value"]), str(value.get("currency") or "").upper()


def browse_search_to_records(payload, *, observed_at=None):
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dictionary")
    observed_at = observed_at or datetime.now(timezone.utc).isoformat()
    records, rejected = [], []
    for index, item in enumerate(payload.get("itemSummaries") or []):
        try:
            price, currency = _money(item.get("price"))
            item_id = str(item.get("itemId") or "").strip()
            title = str(item.get("title") or "").strip()
            if not item_id or not title or not currency:
                raise ValueError("itemId, title, and price currency are required")
            category = str((item.get("categories") or [{}])[0].get("categoryName") or "unknown")
            records.append({
                "external_id": item_id,
                "name": title,
                "category": category,
                "source": "ebay_browse",
                "source_url": item.get("itemWebUrl"),
                "currency": currency,
                "purchase_price": price,
                # Search listings are asking-price evidence, not observed resale outcomes.
                "expected_sale_price": price,
                "sale_probability": 0.0,
                "confidence": 0.0,
                "evidence_count": 1,
                "observed_at": observed_at,
                "metadata": {
                    "provider": "ebay",
                    "adapter_version": EBAY_BROWSE_ADAPTER_VERSION,
                    "condition": item.get("condition"),
                    "epid": item.get("epid"),
                    "gtin": item.get("gtin"),
                    "model_number": None,
                    "asking_price_only": True,
                },
            })
        except (TypeError, ValueError, IndexError) as exc:
            rejected.append({"index": index, "reason": str(exc)})
    return records, rejected
