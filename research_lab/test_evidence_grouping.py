"""Offline checks for conservative evidence grouping."""

from research_lab.evidence_grouping import estimate_groups, group_evidence
from research_lab.real_market_source_adapter import normalize_raw_observation


def row(external_id, source, price, sale, name="Used Camera"):
    return normalize_raw_observation({
        "external_id": external_id, "name": name, "category": "camera",
        "source": source, "currency": "JPY", "purchase_price": price,
        "expected_sale_price": sale, "sale_probability": 0.7,
        "confidence": 0.6, "evidence_count": 2,
    })


def main():
    observations = [
        row("a", "market-a", 10000, 13000),
        row("b", "market-b", 11000, 14000, " used camera "),
        row("c", "market-c", 5000, 7000, "Other Camera"),
    ]
    groups = group_evidence(observations)
    assert len(groups) == 2
    estimates = estimate_groups(observations)
    assert len(estimates) == 2
    used = next(x for x in estimates if x.name.strip().casefold() == "used camera")
    assert used.purchase_price == 10500
    assert used.expected_sale_price == 13500
    assert used.source_count == 2
    assert used.evidence_count == 4
    print("evidence grouping tests passed")


if __name__ == "__main__":
    main()
