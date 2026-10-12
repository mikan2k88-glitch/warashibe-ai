from __future__ import annotations


DEFAULT_BUDGET = {
    "max_supplier_items": 20,
    "max_market_queries": 10,
    "max_market_quotes_per_query": 20,
}


def normalize_source_budget(payload: dict | None = None) -> dict:
    config = {**DEFAULT_BUDGET, **dict(payload or {})}
    return {
        "max_supplier_items": min(200, max(1, int(config["max_supplier_items"]))),
        "max_market_queries": min(100, max(1, int(config["max_market_queries"]))),
        "max_market_quotes_per_query": min(200, max(1, int(config["max_market_quotes_per_query"]))),
    }
