from __future__ import annotations

from datetime import datetime, timezone


class MarketQuoteCache:
    def __init__(self):
        self._items = {}

    def get(self, query: str):
        row = self._items.get(query)
        return list(row["quotes"]) if row else None

    def put(self, query: str, quotes: list[dict]):
        self._items[query] = {
            "quotes": [dict(row) for row in quotes],
            "stored_at": datetime.now(timezone.utc).isoformat(),
        }

    def stats(self) -> dict:
        return {"entries": len(self._items)}
