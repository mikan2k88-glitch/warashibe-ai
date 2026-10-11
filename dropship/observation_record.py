from __future__ import annotations

from .dedupe import observation_fingerprint


def build_observation_record(row: dict) -> dict:
    item = dict(row)
    fingerprint = item.get("observation_fingerprint") or observation_fingerprint(item)
    return {
        "product_key": str(item.get("product_key") or "unknown"),
        "supplier": item.get("supplier"),
        "source": item.get("source"),
        "observed_at": item.get("observed_at"),
        "observation_fingerprint": fingerprint,
        "observation": item,
    }
