"""Offline checks for conservative cross-market identity resolution."""

from research_lab.market_identity_resolution import identity_key, same_identity
from research_lab.real_market_source_adapter import normalize_raw_observation


def obs(external_id, name, source, metadata=None):
    return normalize_raw_observation({
        "external_id": external_id, "name": name, "category": "console",
        "source": source, "currency": "JPY", "purchase_price": 30000,
        "expected_sale_price": 35000, "sale_probability": 0.7,
        "confidence": 0.7, "evidence_count": 2, "metadata": metadata or {},
    })


def main():
    a = obs("a", "Nintendo Switch OLED White", "market-a", {"model_number": "HEG-S-KAAAA"})
    b = obs("b", "Switch 有機EL ホワイト", "market-b", {"model_number": "heg-s-kaaaa"})
    c = obs("c", "Nintendo Switch OLED White", "market-c", {"model_number": "DIFFERENT"})
    d = obs("d", "Nintendo Switch OLED White", "market-d")
    e = obs("e", " Nintendo　Switch OLED White ", "market-e")

    assert same_identity(a, b)
    assert not same_identity(a, c)
    assert not same_identity(a, d)
    assert same_identity(d, e)
    assert identity_key(a)[0] == "model_number"
    print("market identity resolution tests passed")


if __name__ == "__main__":
    main()
