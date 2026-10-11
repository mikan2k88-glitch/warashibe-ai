from __future__ import annotations

from datetime import datetime, timezone


FIELD_ALIASES = {
    "product_key": ("product_key", "sku", "id", "variant_id"),
    "name": ("name", "title", "product_name"),
    "sale_price": ("sale_price", "price", "retail_price"),
    "supplier_cost": ("supplier_cost", "cost", "wholesale_price"),
    "supplier_shipping": ("supplier_shipping", "shipping", "shipping_cost"),
    "delivery_days": ("delivery_days", "lead_time_days", "shipping_days"),
    "inventory_confirmed": ("inventory_confirmed", "in_stock", "available"),
}


def _first(row: dict, names, default=None):
    for name in names:
        if name in row and row[name] is not None:
            return row[name]
    return default


def normalize_provider_row(row: dict, *, provider_name: str) -> dict:
    observed_at = row.get("observed_at") or datetime.now(timezone.utc).isoformat()
    result = dict(row)
    for target, aliases in FIELD_ALIASES.items():
        result[target] = _first(row, aliases, result.get(target))
    result["product_key"] = str(result.get("product_key") or "unknown")
    result["name"] = str(result.get("name") or "unknown")
    result["source"] = str(row.get("source") or provider_name)
    result["observed_at"] = str(observed_at)
    result["provider_name"] = provider_name
    return result
