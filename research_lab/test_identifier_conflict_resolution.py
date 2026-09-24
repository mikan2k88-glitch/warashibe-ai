"""Offline checks for deterministic identifier conflict handling."""

from research_lab.identifier_conflict_resolution import assess_identity_conflicts
from research_lab.real_market_source_adapter import normalize_raw_observation


def obs(external_id, metadata):
    return normalize_raw_observation({
        "external_id": external_id, "name": "Product", "category": "test", "source": "fixture",
        "currency": "JPY", "purchase_price": 100, "expected_sale_price": 150,
        "sale_probability": 0.7, "confidence": 0.7, "evidence_count": 1, "metadata": metadata,
    })


def main():
    gtin = "09521234000006"
    a = obs("a", {"gtin": gtin, "model_number": "MODEL-A"})
    b = obs("b", {"ean": gtin, "model_number": "model-a"})
    good = assess_identity_conflicts(a, b)
    assert good.safe_to_merge and good.conflicts == ()

    c = obs("c", {"upc": gtin, "model_number": "MODEL-B"})
    bad = assess_identity_conflicts(a, c)
    assert not bad.safe_to_merge
    assert bad.conflicts == ("model_number",)

    no_shared = assess_identity_conflicts(a, obs("d", {"isbn": "9780306406157"}))
    assert not no_shared.safe_to_merge
    print("identifier conflict resolution tests passed")


if __name__ == "__main__":
    main()
