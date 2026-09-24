"""Conservative identity resolution for cross-market observations.

Only deterministic identifiers and normalized text are used here. Ambiguous
matches remain separate; no AI/fuzzy guess is allowed to merge market evidence.
"""

import re
import unicodedata

from research_lab.real_market_schema import MarketObservation

IDENTITY_VERSION = "0.1"


def normalize_identity_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", str(value)).casefold()
    return "".join(re.findall(r"[\w]+", text, flags=re.UNICODE))


def identity_key(observation: MarketObservation) -> tuple[str, str, str]:
    metadata = observation.metadata or {}
    for field in ("gtin", "ean", "upc", "isbn", "model_number"):
        value = metadata.get(field)
        if value not in (None, ""):
            return (field, normalize_identity_text(value), observation.currency.upper())
    return (
        "text",
        normalize_identity_text(observation.name) + ":" + normalize_identity_text(observation.category),
        observation.currency.upper(),
    )


def same_identity(left: MarketObservation, right: MarketObservation) -> bool:
    """Fail closed: only equal deterministic keys are treated as the same item."""
    return identity_key(left) == identity_key(right)
