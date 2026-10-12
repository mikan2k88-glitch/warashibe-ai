from __future__ import annotations

import re


def build_market_query(candidate: dict) -> str:
    name = str(candidate.get("name") or "").strip()
    sku = str((candidate.get("metadata") or {}).get("sku") or candidate.get("sku") or "").strip()
    query = name or sku
    query = re.sub(r"\s+", " ", query).strip()
    return query[:200]


def group_quotes_by_product(quote_rows: list[dict]) -> dict[str, list[dict]]:
    grouped = {}
    for row in quote_rows:
        key = str(row.get("product_key") or "")
        if not key:
            continue
        grouped.setdefault(key, []).extend(
            quote for quote in (row.get("quotes") or []) if isinstance(quote, dict)
        )
    return grouped
