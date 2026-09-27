"""Deterministic end-to-end market decision pipeline check."""

from research_lab.end_to_end_market_decision_pipeline import run_market_decision


class FixtureProvider:
    name = "fixture-market"

    def fetch(self, query):
        assert query == "camera"
        base = {
            "name": "Camera A", "category": "camera", "currency": "JPY",
            "purchase_price": 10000, "expected_sale_price": 14000,
            "sale_probability": .75, "confidence": .8, "evidence_count": 2,
            "estimated_days_to_sale": 3, "recovery_value": 7000,
            "metadata": {"gtin": "09521234000006", "model_number": "CAM-A"},
        }
        rows = []
        for source, price in (("market-a", 10000), ("market-b", 10500)):
            row = dict(base)
            row.update({"external_id": source, "source": source, "purchase_price": price})
            rows.append(row)
        return rows


def main():
    run = run_market_decision(
        FixtureProvider(), "camera", 11000,
        min_confidence=.5, min_evidence_count=3, min_source_count=2,
    )
    assert run.raw_count == 2
    assert run.normalized_count == 2
    assert run.estimate_count == 1
    assert run.decision["quality_accepted"] == 1
    assert run.decision["quality_rejected"] == 0
    assert run.decision["input_estimates"] == 1
    class MixedProvider(FixtureProvider):
        def fetch(self, query):
            rows = super().fetch(query)
            return [rows[0], None, {**rows[0], "metadata": []}, rows[1],
                    {**rows[0], "purchase_price": 10 ** 1000}]

    mixed = run_market_decision(
        MixedProvider(), " camera ", 11000,
        min_confidence=.5, min_evidence_count=3, min_source_count=2,
    )
    assert mixed.provider == "fixture-market"
    assert mixed.query == "camera"
    assert mixed.raw_count == 5
    assert mixed.normalized_count == 2
    assert mixed.normalization_rejected == 3
    assert mixed.estimate_count == 1
    assert mixed.decision["quality_accepted"] == 1
    assert mixed.decision["quality_rejected"] == 0
    assert mixed.decision["input_estimates"] == 1

    print("end-to-end market decision pipeline tests passed")


if __name__ == "__main__":
    main()
