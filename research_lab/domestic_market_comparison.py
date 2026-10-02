"""Conservative domestic cross-market price comparison for PG-013.

Only observations that resolve to the same deterministic identity are compared.
No fuzzy matching or commerce action is performed.
"""

from research_lab.market_identity_resolution import identity_key, same_identity
from research_lab.real_market_schema import MarketObservation, validate_observation

COMPARISON_VERSION = "0.1"


def compare_domestic_observations(left: MarketObservation, right: MarketObservation) -> dict:
    left_errors = validate_observation(left)
    right_errors = validate_observation(right)
    if left_errors or right_errors:
        raise ValueError("invalid market observation")

    left_key = identity_key(left)
    right_key = identity_key(right)
    matched = same_identity(left, right)

    base = {
        "version": COMPARISON_VERSION,
        "same_identity": matched,
        "identity_type": left_key[0] if matched else None,
        "identity_value": left_key[1] if matched else None,
        "currency": left.currency.upper() if matched else None,
        "commerce_authorized": False,
        "external_action_authorized": False,
    }

    if not matched:
        return dict(
            base,
            status="identity_mismatch",
            lowest_asking_price_jpy=None,
            lowest_asking_source=None,
            highest_asking_price_jpy=None,
            price_spread_jpy=None,
        )

    if left.currency.upper() != "JPY" or right.currency.upper() != "JPY":
        raise ValueError("domestic comparison requires JPY observations")

    pairs = [
        (float(left.purchase_price), left.source),
        (float(right.purchase_price), right.source),
    ]
    lowest_price, lowest_source = min(pairs, key=lambda row: row[0])
    highest_price, _ = max(pairs, key=lambda row: row[0])

    return dict(
        base,
        status="comparison_ready",
        lowest_asking_price_jpy=lowest_price,
        lowest_asking_source=lowest_source,
        highest_asking_price_jpy=highest_price,
        price_spread_jpy=highest_price - lowest_price,
        sources=(left.source, right.source),
    )
