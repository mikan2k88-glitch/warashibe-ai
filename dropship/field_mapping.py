from __future__ import annotations


DEFAULT_MAPPING = {
    "product_key": "product_key",
    "name": "name",
    "supplier": "supplier",
    "category": "category",
    "sale_price": "sale_price",
    "supplier_cost": "supplier_cost",
    "supplier_shipping": "supplier_shipping",
    "delivery_days": "delivery_days",
    "inventory_confirmed": "inventory_confirmed",
    "supplier_allows_dropshipping": "supplier_allows_dropshipping",
    "platform_terms_confirmed": "platform_terms_confirmed",
    "supplier_reliable": "supplier_reliable",
}


def _get_path(row: dict, path: str):
    value = row
    for part in str(path).split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def apply_field_mapping(row: dict, mapping: dict | None = None) -> dict:
    config = {**DEFAULT_MAPPING, **dict(mapping or {})}
    output = {}
    for target, source in config.items():
        if not source:
            continue
        output[target] = _get_path(row, source)
    for key in ("source", "observed_at", "metadata"):
        if key in row:
            output[key] = row[key]
    return output


def validate_field_mapping(mapping: dict) -> dict:
    required = {"product_key", "name", "sale_price", "supplier_cost"}
    missing = sorted(key for key in required if not mapping.get(key))
    return {
        "valid": not missing,
        "missing_required_targets": missing,
        "write_capable": False,
    }
