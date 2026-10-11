from __future__ import annotations

import hashlib
import json


def observation_fingerprint(row: dict) -> str:
    stable = {
        "product_key": str(row.get("product_key") or ""),
        "supplier": str(row.get("supplier") or ""),
        "source": str(row.get("source") or ""),
        "sale_price": row.get("sale_price"),
        "supplier_cost": row.get("supplier_cost"),
        "inventory_confirmed": row.get("inventory_confirmed"),
        "delivery_days": row.get("delivery_days"),
    }
    raw = json.dumps(stable, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def deduplicate_observations(rows: list[dict]) -> dict:
    seen = set()
    unique = []
    duplicates = []
    for row in rows:
        fp = observation_fingerprint(row)
        enriched = {**row, "observation_fingerprint": fp}
        if fp in seen:
            duplicates.append(enriched)
            continue
        seen.add(fp)
        unique.append(enriched)
    return {
        "unique": unique,
        "duplicates": duplicates,
        "unique_count": len(unique),
        "duplicate_count": len(duplicates),
    }
