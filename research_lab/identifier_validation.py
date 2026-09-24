"""Offline validation for deterministic product identifiers.

GTIN validation follows the GS1 fixed-length numeric/check-digit rules. This
module deliberately performs no network lookup: structural validity is not a
claim that GS1 assigned the identifier.
"""

GTIN_LENGTHS = frozenset({8, 12, 13, 14})


def normalize_gtin(value: object) -> str:
    """Return digits only when the supplied GTIN has an accepted GS1 length."""
    text = str(value).strip()
    return text if text.isascii() and text.isdigit() and len(text) in GTIN_LENGTHS else ""


def calculate_gtin_check_digit(body: str) -> str:
    """Calculate the GS1 check digit for a GTIN body (all digits except last)."""
    if not body or not body.isascii() or not body.isdigit():
        raise ValueError("GTIN body must contain ASCII digits only")
    total = sum(int(digit) * (3 if offset % 2 == 0 else 1)
                for offset, digit in enumerate(reversed(body)))
    return str((-total) % 10)


def is_valid_gtin(value: object) -> bool:
    gtin = normalize_gtin(value)
    return bool(gtin) and calculate_gtin_check_digit(gtin[:-1]) == gtin[-1]


def normalize_isbn(value: object) -> str:
    """Normalize ISBN-10/13 text; separators are ignored, other characters fail."""
    text = str(value).strip().replace("-", "").replace(" ", "")
    if len(text) == 10 and text[:9].isascii() and text[:9].isdigit() and (text[-1].isdigit() or text[-1] in "Xx"):
        return text[:9] + text[-1].upper()
    if len(text) == 13 and text.isascii() and text.isdigit():
        return text
    return ""


def is_valid_isbn(value: object) -> bool:
    """Validate ISBN-10 or ISBN-13 check digits offline."""
    isbn = normalize_isbn(value)
    if len(isbn) == 10:
        total = sum((10 - i) * (10 if ch == "X" else int(ch)) for i, ch in enumerate(isbn))
        return total % 11 == 0
    if len(isbn) == 13:
        total = sum(int(ch) * (1 if i % 2 == 0 else 3) for i, ch in enumerate(isbn[:12]))
        return str((-total) % 10) == isbn[-1]
    return False
