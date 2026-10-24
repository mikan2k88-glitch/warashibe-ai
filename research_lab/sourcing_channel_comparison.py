"""P2 Candidate Search v2.5: read-only sourcing-channel comparison.

The comparator ranks *fully-loaded acquisition cost*, not sticker price.
It accepts already-observed source offers from domestic shops/marketplaces and
future Amazon adapters, normalizes them into one contract, and preserves the
Human Gate. It performs no network I/O and no commerce action.
"""

from dataclasses import asdict, dataclass
from typing import Any, Iterable

COMPARATOR_VERSION = "2.5"
DEFAULT_MIN_SOURCE_CONFIDENCE = 60

SUPPORTED_SOURCE_CHANNELS = {
    "surugaya",
    "netoff",
    "bookoff",
    "geo",
    "hardoff",
    "lashinbang",
    "mercari_shops",
    "yahoo",
    "specialty_shop",
    "manufacturer_shop",
    # Amazon/Keepa is implemented but may remain operationally disabled until
    # the user chooses to fund/configure the external API.
    "amazon_keepa_jp",
}


def _money(value: Any, name: str, *, allow_none: bool = False) -> int | None:
    if value is None and allow_none:
        return None
    if value is None or isinstance(value, bool):
        raise ValueError(f"{name} must be a non-negative number")
    try:
        parsed = int(round(float(value)))
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a non-negative number") from None
    if parsed < 0:
        raise ValueError(f"{name} must be >= 0")
    return parsed


def _confidence(value: Any) -> int:
    if isinstance(value, bool):
        raise ValueError("source_confidence must be between 0 and 100")
    try:
        parsed = int(round(float(value)))
    except (TypeError, ValueError):
        raise ValueError("source_confidence must be between 0 and 100") from None
    if parsed < 0 or parsed > 100:
        raise ValueError("source_confidence must be between 0 and 100")
    return parsed


@dataclass(frozen=True)
class SourceOffer:
    identity_key: str
    source_channel: str
    source_name: str
    item_price_jpy: int
    inbound_shipping_jpy: int | None
    source_handling_fee_jpy: int
    other_acquisition_cost_jpy: int
    total_acquisition_jpy: int | None
    in_stock: bool
    identity_verified: bool
    condition_match: bool
    source_confidence: int
    observed_at: str | None = None
    source_url: str | None = None
    notes: str | None = None
    human_gate_required: bool = True
    external_execution_authorized: bool = False
    purchase_authorized: bool = False


def normalize_source_offer(raw: dict[str, Any]) -> SourceOffer:
    """Normalize one source observation into the v2.5 comparison contract."""
    if not isinstance(raw, dict):
        raise ValueError("source offer must be a dictionary")

    identity = str(raw.get("identity_key") or "").strip()
    if not identity:
        raise ValueError("identity_key is required")

    channel = str(raw.get("source_channel") or "").strip().lower()
    if channel not in SUPPORTED_SOURCE_CHANNELS:
        raise ValueError(f"unsupported source_channel: {channel or '<empty>'}")

    source_name = str(raw.get("source_name") or channel).strip()
    if not source_name:
        raise ValueError("source_name is required")

    item = _money(raw.get("item_price_jpy"), "item_price_jpy")
    shipping = _money(
        raw.get("inbound_shipping_jpy"),
        "inbound_shipping_jpy",
        allow_none=True,
    )
    handling = _money(
        raw.get("source_handling_fee_jpy", 0),
        "source_handling_fee_jpy",
    )
    other = _money(
        raw.get("other_acquisition_cost_jpy", 0),
        "other_acquisition_cost_jpy",
    )
    total = None if shipping is None else item + shipping + handling + other

    return SourceOffer(
        identity_key=identity,
        source_channel=channel,
        source_name=source_name,
        item_price_jpy=item,
        inbound_shipping_jpy=shipping,
        source_handling_fee_jpy=handling,
        other_acquisition_cost_jpy=other,
        total_acquisition_jpy=total,
        in_stock=raw.get("in_stock") is True,
        identity_verified=raw.get("identity_verified") is True,
        condition_match=raw.get("condition_match") is True,
        source_confidence=_confidence(raw.get("source_confidence", 0)),
        observed_at=raw.get("observed_at"),
        source_url=raw.get("source_url"),
        notes=raw.get("notes"),
    )


def amazon_observation_to_source_offer(
    observation: dict[str, Any],
    *,
    identity_key: str,
    prime_member: bool = False,
    condition_match: bool = True,
) -> SourceOffer:
    """Bridge a v2.4 Amazon observation into the v2.5 source contract.

    The function is safe even while Keepa live access is deferred: callers can
    use deterministic observations and later enable the external adapter
    without changing comparison logic.
    """
    total_key = (
        "total_acquisition_prime_jpy"
        if prime_member
        else "total_acquisition_non_prime_jpy"
    )
    total = observation.get(total_key)
    price = _money(observation.get("price_jpy"), "price_jpy")
    shipping = observation.get("shipping_jpy")
    shipping = _money(shipping, "shipping_jpy", allow_none=True)

    # For Prime-exclusive offers the selected total can differ from
    # price+shipping. Preserve the authoritative observed total as "other"
    # adjustment only when it is non-negative and known.
    other = 0
    if total is not None and shipping is not None:
        selected_total = _money(total, total_key)
        delta = selected_total - price - shipping
        if delta < 0:
            # Prime-exclusive discount is represented by the effective item
            # price so total acquisition remains internally consistent.
            price = max(0, selected_total - shipping)
        else:
            other = delta

    return normalize_source_offer(
        {
            "identity_key": identity_key,
            "source_channel": "amazon_keepa_jp",
            "source_name": "Amazon.co.jp / Keepa",
            "item_price_jpy": price,
            "inbound_shipping_jpy": shipping,
            "source_handling_fee_jpy": 0,
            "other_acquisition_cost_jpy": other,
            "in_stock": observation.get("in_stock") is True,
            "identity_verified": bool(observation.get("asin")),
            "condition_match": condition_match,
            "source_confidence": observation.get("source_confidence", 0),
            "observed_at": observation.get("observed_at"),
            "notes": (
                "prime_member_scenario"
                if prime_member
                else "non_prime_scenario"
            ),
        }
    )


def assess_source_offer(
    offer: SourceOffer,
    *,
    capital_jpy: int,
    max_total_acquisition_jpy: int | None = None,
    min_source_confidence: int = DEFAULT_MIN_SOURCE_CONFIDENCE,
) -> dict[str, Any]:
    """Apply source-integrity/capital gates without authorizing commerce."""
    capital = _money(capital_jpy, "capital_jpy")
    ceiling = (
        capital
        if max_total_acquisition_jpy is None
        else min(capital, _money(max_total_acquisition_jpy, "max_total_acquisition_jpy"))
    )

    if offer.total_acquisition_jpy is None:
        status, reason = "rejected", "shipping_loss"
    elif not offer.in_stock:
        status, reason = "rejected", "source_unavailable"
    elif not offer.identity_verified:
        status, reason = "rejected", "edition_mismatch"
    elif not offer.condition_match:
        status, reason = "rejected", "condition_mismatch"
    elif offer.source_confidence < min_source_confidence:
        status, reason = "rejected", "stale_evidence"
    elif offer.total_acquisition_jpy > capital:
        status, reason = "rejected", "over_capital"
    elif offer.total_acquisition_jpy > ceiling:
        status, reason = "rejected", "insufficient_margin"
    else:
        status, reason = "source_eligible", "source_gate_passed"

    return {
        "version": COMPARATOR_VERSION,
        "status": status,
        "reason": reason,
        "identity_key": offer.identity_key,
        "source_channel": offer.source_channel,
        "source_name": offer.source_name,
        "item_price_jpy": offer.item_price_jpy,
        "inbound_shipping_jpy": offer.inbound_shipping_jpy,
        "source_handling_fee_jpy": offer.source_handling_fee_jpy,
        "other_acquisition_cost_jpy": offer.other_acquisition_cost_jpy,
        "total_acquisition_jpy": offer.total_acquisition_jpy,
        "source_confidence": offer.source_confidence,
        "capital_jpy": capital,
        "max_total_acquisition_jpy": ceiling,
        "human_gate_required": True,
        "external_execution_authorized": False,
        "purchase_authorized": False,
    }


def compare_source_offers(
    offers: Iterable[SourceOffer | dict[str, Any]],
    *,
    capital_jpy: int,
    max_total_acquisition_jpy: int | None = None,
    min_source_confidence: int = DEFAULT_MIN_SOURCE_CONFIDENCE,
) -> dict[str, Any]:
    """Rank eligible suppliers for one exact item by fully-loaded acquisition."""
    normalized = [
        item if isinstance(item, SourceOffer) else normalize_source_offer(item)
        for item in offers
    ]
    if not normalized:
        raise ValueError("at least one source offer is required")

    identities = {item.identity_key for item in normalized}
    if len(identities) != 1:
        raise ValueError("all source offers must share the same identity_key")

    assessed = [
        assess_source_offer(
            item,
            capital_jpy=capital_jpy,
            max_total_acquisition_jpy=max_total_acquisition_jpy,
            min_source_confidence=min_source_confidence,
        )
        for item in normalized
    ]
    eligible = [row for row in assessed if row["status"] == "source_eligible"]
    eligible.sort(
        key=lambda row: (
            row["total_acquisition_jpy"],
            -row["source_confidence"],
            row["source_name"],
        )
    )
    rejected = [row for row in assessed if row["status"] != "source_eligible"]

    best = eligible[0] if eligible else None
    return {
        "version": COMPARATOR_VERSION,
        "status": "comparison_ready" if best else "no_eligible_source",
        "identity_key": normalized[0].identity_key,
        "source_offer_count": len(normalized),
        "eligible_source_count": len(eligible),
        "rejected_source_count": len(rejected),
        "best_source": best,
        "eligible_sources": eligible,
        "rejected_sources": rejected,
        "ranking_basis": "fully_loaded_total_acquisition_then_confidence",
        "human_gate_required": True,
        "external_execution_authorized": False,
        "purchase_authorized": False,
    }
