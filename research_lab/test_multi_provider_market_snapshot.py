"""Checks for combining read-only evidence from multiple providers."""

from research_lab.multi_provider_market_snapshot import capture_market_snapshot


class Provider:
    def __init__(self, name, price):
        self.name, self.price = name, price

    def fetch(self, query):
        return [{
            "external_id": self.name, "name": "Camera A", "category": "camera",
            "source": self.name, "currency": "JPY", "purchase_price": self.price,
            "expected_sale_price": 14000, "sale_probability": .75,
            "confidence": .8, "evidence_count": 2, "estimated_days_to_sale": 3,
            "recovery_value": 7000,
            "metadata": {"gtin": "09521234000006", "model_number": "CAM-A"},
        }]


def main():
    snapshot = capture_market_snapshot(
        [Provider("market-a", 10000), Provider("market-b", 10500)], "camera"
    )
    assert snapshot.provider_count == 2
    assert snapshot.raw_count == 2
    assert snapshot.rejected_count == 0
    assert len(snapshot.observations) == 2
    assert {row.source for row in snapshot.observations} == {"market-a", "market-b"}
    print("multi-provider market snapshot tests passed")


if __name__ == "__main__":
    main()
