from __future__ import annotations


def next_page_url(payload, *, current_url: str | None = None) -> str | None:
    if isinstance(payload, dict):
        for key in ("next", "next_url", "nextPage", "next_page"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
        pagination = payload.get("pagination")
        if isinstance(pagination, dict):
            for key in ("next", "next_url"):
                value = pagination.get(key)
                if isinstance(value, str) and value:
                    return value
    return None


def extract_items(payload) -> list[dict]:
    if isinstance(payload, list):
        return [dict(row) for row in payload if isinstance(row, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("offers", "items", "products", "results", "data"):
        value = payload.get(key)
        if isinstance(value, list):
            return [dict(row) for row in value if isinstance(row, dict)]
        if isinstance(value, dict):
            for nested_key in ("items", "products", "results"):
                nested = value.get(nested_key)
                if isinstance(nested, list):
                    return [dict(row) for row in nested if isinstance(row, dict)]
    return []
