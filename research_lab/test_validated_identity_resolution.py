"""Checks that only structurally valid GTIN-family values drive identity."""

from research_lab.market_identity_resolution import identity_key, same_identity
from research_lab.real_market_source_adapter import normalize_raw_observation


def obs(external_id, source, metadata):
    return normalize_raw_observation({
        "external_id": external_id, "name": "Same Product", "category": "test",
        "source": source, "currency": "JPY", "purchase_price": 100,
        "expected_sale_price": 150, "sale_probability": 0.7,
        "confidence": 0.7, "evidence_count": 1, "metadata": metadata,
    })


def main():
    valid = "09521234000006"
    a = obs("a", "market-a", {"gtin": valid})
    b = obs("b", "market-b", {"ean": valid})
    assert same_identity(a, b)
    assert identity_key(a)[0] == "gtin"

    # Same invalid barcode-like value must not become a deterministic identity.
    bad_a = obs("c", "market-a", {"gtin": "09521234000007", "model_number": "A"})
    bad_b = obs("d", "market-b", {"gtin": "09521234000007", "model_number": "B"})
    assert not same_identity(bad_a, bad_b)
    assert identity_key(bad_a)[0] == "model_number"

    # Invalid GTIN falls through safely to text when no other identifier exists.
    fallback = obs("e", "market-c", {"upc": "not-a-gtin"})
    assert identity_key(fallback)[0] == "text"
    print("validated identity resolution tests passed")


if __name__ == "__main__":
    main()
