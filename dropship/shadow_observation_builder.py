from __future__ import annotations

from datetime import datetime, timezone


def build_opportunity_observations(real_read_result: dict) -> list[dict]:
    observed_at = datetime.now(timezone.utc).isoformat()
    rows = []
    for opportunity in (real_read_result.get("ranking") or {}).get("ranked") or []:
        candidate = opportunity.get("candidate") or {}
        economics = opportunity.get("economics") or {}
        rows.append({
            "product_key": opportunity.get("product_key") or candidate.get("product_key"),
            "name": candidate.get("name"),
            "supplier": candidate.get("supplier"),
            "category": candidate.get("category"),
            "source": "real-read-opportunity",
            "sale_price": candidate.get("sale_price"),
            "supplier_cost": candidate.get("supplier_cost"),
            "supplier_shipping": candidate.get("supplier_shipping"),
            "inventory_confirmed": candidate.get("inventory_confirmed"),
            "delivery_days": candidate.get("delivery_days"),
            "opportunity_score": opportunity.get("opportunity_score"),
            "expected_net_profit": economics.get("net_profit"),
            "margin": economics.get("margin"),
            "market_quote_count": opportunity.get("market_quote_count"),
            "promotion_ready": opportunity.get("promotion_ready") is True,
            "observed_at": observed_at,
        })
    return rows
