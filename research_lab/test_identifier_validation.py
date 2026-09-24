"""Offline checks for GS1-compatible GTIN structural validation."""

from research_lab.identifier_validation import (
    calculate_gtin_check_digit,
    is_valid_gtin,
    normalize_gtin,
)


def main():
    # GS1-published example GTIN.
    assert is_valid_gtin("09521234000006")
    assert is_valid_gtin(" 09521234000006 ")
    assert not is_valid_gtin("09521234000007")
    assert not is_valid_gtin("9521234000007")  # valid length, wrong check digit
    assert not is_valid_gtin("123456789")
    assert not is_valid_gtin("ABC12345")
    assert normalize_gtin("１２３４５６７８") == ""  # reject lookalike Unicode digits
    assert calculate_gtin_check_digit("0952123400000") == "6"
    print("identifier validation tests passed")


if __name__ == "__main__":
    main()
