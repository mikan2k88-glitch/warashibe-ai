"""Offline checks for conflict-aware evidence grouping."""

from research_lab.conflict_aware_evidence_grouping import group_conflict_aware
from research_lab.real_market_source_adapter import normalize_raw_observation


def obs(key, model):
    return normalize_raw_observation({
        "external_id": key, "name": "Product", "category": "test", "source": key,
        "currency": "JPY", "purchase_price": 100, "expected_sale_price": 150,
        "sale_probability": 0.7, "confidence": 0.7, "evidence_count": 1,
        "metadata": {"gtin": "09521234000006", "model_number": model},
    })


def main():
    rows = [obs("a", "MODEL-A"), obs("b", "model-a"), obs("c", "MODEL-B")]
    groups = group_conflict_aware(rows)
    assert sorted(len(group) for group in groups) == [1, 2]
    merged = next(group for group in groups if len(group) == 2)
    assert {x.external_id for x in merged} == {"a", "b"}
    print("conflict-aware evidence grouping tests passed")


if __name__ == "__main__":
    main()
