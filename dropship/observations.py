from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone


def _parse_time(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def summarize_observations(rows: list[dict]) -> dict:
    groups = defaultdict(list)
    for row in rows:
        key = str(row.get("product_key") or row.get("sku") or row.get("name") or "unknown")
        groups[key].append(row)

    products = []
    for product_key, observations in groups.items():
        ordered = sorted(
            observations,
            key=lambda row: _parse_time(row.get("observed_at")) or datetime.min.replace(tzinfo=timezone.utc),
        )
        prices = [float(row.get("sale_price") or 0) for row in ordered if float(row.get("sale_price") or 0) > 0]
        costs = [float(row.get("supplier_cost") or 0) for row in ordered if float(row.get("supplier_cost") or 0) > 0]
        inventories = [row.get("inventory_confirmed") is True for row in ordered]
        deliveries = [int(row.get("delivery_days") or 0) for row in ordered if int(row.get("delivery_days") or 0) > 0]
        observed_dates = {
            dt.date().isoformat()
            for dt in (_parse_time(row.get("observed_at")) for row in ordered)
            if dt is not None
        }
        products.append({
            "product_key": product_key,
            "observations": len(ordered),
            "observation_days": len(observed_dates),
            "latest": ordered[-1] if ordered else None,
            "sale_price_min": min(prices) if prices else 0,
            "sale_price_max": max(prices) if prices else 0,
            "supplier_cost_min": min(costs) if costs else 0,
            "supplier_cost_max": max(costs) if costs else 0,
            "inventory_confirmation_rate": round(sum(inventories) / len(inventories), 6) if inventories else 0,
            "max_delivery_days": max(deliveries) if deliveries else 0,
        })

    products.sort(key=lambda row: (-row["observations"], row["product_key"]))
    return {
        "status": "ok",
        "total_observations": len(rows),
        "product_count": len(products),
        "products": products,
    }
