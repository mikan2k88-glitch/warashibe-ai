"""Offline checks for provider-to-ingestion composition."""

from research_lab.provider_ingestion_pipeline import ingest_query


class FakeProvider:
    name = "fixture-market"

    def fetch(self, query):
        assert query == "used camera"
        return [{
            "external_id": "listing-1", "name": "Used camera", "category": "camera",
            "source": self.name, "currency": "JPY", "purchase_price": 10000,
            "expected_sale_price": 13000, "sale_probability": 0.7,
            "confidence": 0.6, "evidence_count": 2,
        }, {"external_id": "bad"}]


def main():
    result = ingest_query(FakeProvider(), " used camera ")
    assert result.provider == "fixture-market"
    assert result.raw_count == 2
    assert result.accepted_count == 1
    assert result.rejected_count == 1
    assert result.accepted[0].name == "Used camera"
    print("provider ingestion pipeline tests passed")


if __name__ == "__main__":
    main()
