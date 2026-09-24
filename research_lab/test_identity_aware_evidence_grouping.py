"""Offline checks for identity-aware evidence grouping."""

from research_lab.identity_aware_evidence_grouping import estimate_identity_groups, group_by_identity
from research_lab.real_market_source_adapter import normalize_raw_observation


def obs(external_id, source, price, sale, model):
    return normalize_raw_observation({
        "external_id": external_id, "name": "Console " + external_id,
        "category": "console", "source": source, "currency": "JPY",
        "purchase_price": price, "expected_sale_price": sale,
        "sale_probability": 0.7, "confidence": 0.7, "evidence_count": 2,
        "metadata": {"model_number": model},
    })


def main():
    observations = [
        obs("a", "market-a", 30000, 36000, "HEG-S-KAAAA"),
        obs("b", "market-b", 32000, 38000, "heg-s-kaaaa"),
        obs("c", "market-c", 20000, 25000, "different"),
    ]
    groups = group_by_identity(observations)
    assert len(groups) == 2
    estimates = estimate_identity_groups(observations)
    assert len(estimates) == 2
    merged = next(x for x in estimates if x.source_count == 2)
    assert merged.purchase_price == 31000
    assert merged.expected_sale_price == 37000
    assert merged.evidence_count == 4
    print("identity-aware evidence grouping tests passed")


if __name__ == "__main__":
    main()
