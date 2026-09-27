"""Offline checks for the live market evidence ingestion boundary."""

from research_lab.live_market_evidence_ingestion import ingest_provider, ingest_records


GOOD = {
    "external_id": "listing-1",
    "name": "Used camera",
    "category": "camera",
    "source": "fixture-market",
    "currency": "JPY",
    "purchase_price": 10000,
    "expected_sale_price": 13000,
    "sale_probability": 0.7,
    "confidence": 0.6,
    "evidence_count": 2,
}


def main():
    result = ingest_records("fixture", [GOOD, {"external_id": "bad"}])
    assert result.raw_count == 2
    assert result.accepted_count == 1
    assert result.rejected_count == 1
    assert result.accepted[0].currency == "JPY"
    assert result.rejected[0]["external_id"] == "bad"

    # Counts are observations, not values to truncate or coerce from booleans.
    for invalid in (1.5, -1, True, False, "NaN", "Infinity", "not-a-count", None):
        bad = {**GOOD, "external_id": "invalid-count", "evidence_count": invalid}
        checked = ingest_records("fixture", [bad])
        assert checked.accepted_count == 0, invalid
        assert checked.rejected_count == 1, invalid
        assert "evidence_count must be a nonnegative integer" in checked.rejected[0]["reason"]
    for valid in (0, 2, "3"):
        checked = ingest_records("fixture", [{**GOOD, "evidence_count": valid}])
        assert checked.accepted_count == 1, valid
        assert checked.accepted[0].evidence_count == int(valid)

    calls = []
    def fetch():
        calls.append("called")
        return [GOOD]

    injected = ingest_provider("fixture", fetch)
    assert calls == ["called"]
    assert injected.accepted_count == 1
    print("live market evidence ingestion tests passed")


if __name__ == "__main__":
    main()
