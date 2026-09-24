"""Offline checks for the read-only market provider contract."""

from research_lab.market_provider_contract import fetch_provider_records, validate_provider


class FakeProvider:
    name = "fixture-market"

    def __init__(self):
        self.queries = []

    def fetch(self, query):
        self.queries.append(query)
        return [{"external_id": "1", "name": "fixture"}]


class MissingFetch:
    name = "broken"


def main():
    provider = FakeProvider()
    assert validate_provider(provider) == []
    name, rows = fetch_provider_records(provider, " used camera ")
    assert name == "fixture-market"
    assert provider.queries == ["used camera"]
    assert rows[0]["external_id"] == "1"
    assert validate_provider(MissingFetch()) == ["provider fetch(query) is required"]

    try:
        fetch_provider_records(provider, "   ")
    except ValueError as exc:
        assert str(exc) == "query is required"
    else:
        raise AssertionError("blank query must fail closed")

    print("market provider contract tests passed")


if __name__ == "__main__":
    main()
