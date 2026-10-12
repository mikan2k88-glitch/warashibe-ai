from __future__ import annotations


class FixtureMarketProvider:
    provider_name = "fixture-market"

    def __init__(self, quotes_by_query: dict[str, list[dict]] | None = None):
        self.quotes_by_query = {
            str(key): [dict(row) for row in value]
            for key, value in (quotes_by_query or {}).items()
        }

    def search(self, query: str) -> list[dict]:
        return [dict(row) for row in self.quotes_by_query.get(str(query), [])]
