"""Offline checks for ISBN-10/13 validation and identity safety."""

from research_lab.identifier_validation import is_valid_isbn, normalize_isbn
from research_lab.market_identity_resolution import identity_key
from research_lab.real_market_source_adapter import normalize_raw_observation


def obs(isbn):
    return normalize_raw_observation({
        "external_id": str(isbn), "name": "Book", "category": "book", "source": "fixture",
        "currency": "JPY", "purchase_price": 100, "expected_sale_price": 150,
        "sale_probability": 0.7, "confidence": 0.7, "evidence_count": 1,
        "metadata": {"isbn": isbn},
    })


def main():
    assert is_valid_isbn("0-306-40615-2")
    assert normalize_isbn("0-306-40615-2") == "0306406152"
    assert is_valid_isbn("9780306406157")
    assert not is_valid_isbn("9780306406158")
    assert identity_key(obs("9780306406157"))[0] == "isbn"
    assert identity_key(obs("9780306406158"))[0] == "text"
    print("ISBN identifier validation tests passed")


if __name__ == "__main__":
    main()
