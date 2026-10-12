from __future__ import annotations

from collections import defaultdict
from statistics import mean


def build_daily_shadow_summary(rows: list[dict]) -> dict:
    groups = defaultdict(list)
    for row in rows:
        observed_at = str(row.get("observed_at") or "")
        day = observed_at[:10] if len(observed_at) >= 10 else "unknown"
        groups[day].append(row)

    days = []
    for day, values in sorted(groups.items()):
        prices = [float(v.get("sale_price") or 0) for v in values if float(v.get("sale_price") or 0) > 0]
        costs = [float(v.get("supplier_cost") or 0) for v in values if float(v.get("supplier_cost") or 0) > 0]
        days.append({
            "day": day,
            "observations": len(values),
            "unique_products": len({str(v.get("product_key") or "unknown") for v in values}),
            "average_sale_price": round(mean(prices), 2) if prices else 0,
            "average_supplier_cost": round(mean(costs), 2) if costs else 0,
            "inventory_confirmation_rate": round(
                sum(1 for v in values if v.get("inventory_confirmed") is True) / len(values),
                6,
            ) if values else 0,
        })

    return {
        "status": "daily_shadow_summary_ready",
        "day_count": len(days),
        "days": days,
        "live_execution_allowed": False,
    }
