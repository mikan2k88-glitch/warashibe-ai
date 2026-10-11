from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from .price_stability import assess_price_stability


def _day(value) -> str | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.date().isoformat()
    except ValueError:
        return None


def build_shadow_metrics(observations: list[dict]) -> dict:
    groups = defaultdict(list)
    for row in observations:
        key = str(row.get("product_key") or "unknown")
        groups[key].append(row)

    products = []
    for key, rows in groups.items():
        days = {_day(row.get("observed_at")) for row in rows}
        days.discard(None)
        prices = [float(row.get("sale_price") or 0) for row in rows if float(row.get("sale_price") or 0) > 0]
        inventory_values = [row.get("inventory_confirmed") for row in rows if row.get("inventory_confirmed") in {True, False}]
        inventory_rate = (
            sum(1 for value in inventory_values if value is True) / len(inventory_values)
            if inventory_values else 0.0
        )
        products.append({
            "product_key": key,
            "observations": len(rows),
            "observation_days": len(days),
            "inventory_confirmation_rate": round(inventory_rate, 6),
            "price_stability": assess_price_stability(prices),
        })

    products.sort(key=lambda row: (-row["observation_days"], -row["observations"], row["product_key"]))
    return {
        "status": "shadow_metrics_ready",
        "product_count": len(products),
        "total_observations": len(observations),
        "products": products,
        "live_execution_allowed": False,
    }
