"""Read-only Amazon.co.jp sourcing observer backed by Keepa.

P2 v2.4 boundary:
- observe and normalize Amazon offers only;
- never buy, cart, list, pay, or mutate an account;
- keep Prime/non-Prime economics separate;
- never assume "Prime == free": shipping must be present in evidence;
- use offer freshness/live-offer evidence because Keepa can retain stale offers;
- support dependency-injected transport so CI is deterministic and secret-free.

The optional live transport reads KEEPA_API_KEY at call time. No credential is
stored in repository data or emitted in observations.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import json
import os
from statistics import median
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

OBSERVER_VERSION = "2.4"
AMAZON_JP_KEEPA_DOMAIN = 5
DEFAULT_MIN_CONFIDENCE = 70
KEEPA_EPOCH_OFFSET_MINUTES = 21_564_000

CONDITION_NAMES = {
    0: "unknown",
    1: "new",
    2: "used_like_new",
    3: "used_very_good",
    4: "used_good",
    5: "used_acceptable",
    6: "refurbished",
    7: "collectible_like_new",
    8: "collectible_very_good",
    9: "collectible_good",
    10: "collectible_acceptable",
    11: "rental",
}


@dataclass(frozen=True)
class AmazonSourceObservation:
    asin: str
    title: str
    condition: str
    seller_id: str | None
    is_amazon: bool
    is_fba: bool
    is_warehouse_deal: bool
    prime_eligible: bool | None
    prime_exclusive: bool
    price_jpy: int
    prime_exclusive_price_jpy: int | None
    shipping_jpy: int | None
    total_acquisition_non_prime_jpy: int | None
    total_acquisition_prime_jpy: int | None
    observed_at: str
    offer_last_seen_at: str | None
    history_30d_median_jpy: int | None
    history_90d_median_jpy: int | None
    source_confidence: int
    confidence_components: dict[str, int]
    external_execution_authorized: bool = False
    purchase_authorized: bool = False


class KeepaHttpTransport:
    """Minimal GET-only Keepa product transport for amazon.co.jp."""

    endpoint = "https://api.keepa.com/product"

    def __init__(self, api_key: str | None = None, timeout_seconds: int = 20):
        self._api_key = api_key
        self.timeout_seconds = timeout_seconds

    def fetch_product(
        self, asin: str, *, domain: int = AMAZON_JP_KEEPA_DOMAIN
    ) -> dict[str, Any]:
        key = self._api_key or os.environ.get("KEEPA_API_KEY")
        if not key:
            raise RuntimeError("KEEPA_API_KEY is required for live Keepa observation")
        params = {
            "key": key,
            "domain": int(domain),
            "asin": asin,
            "offers": 20,
            "history": 1,
            "stats": 90,
        }
        request = Request(
            f"{self.endpoint}?{urlencode(params)}",
            headers={"Accept-Encoding": "gzip"},
            method="GET",
        )
        with urlopen(request, timeout=self.timeout_seconds) as response:
            body = response.read()
            encoding = (response.headers.get("Content-Encoding") or "").lower()
            if encoding == "gzip":
                import gzip

                body = gzip.decompress(body)
            return json.loads(body.decode("utf-8"))


def _money(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        parsed = int(round(float(value)))
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def _keepa_time_to_datetime(value: Any) -> datetime | None:
    try:
        minutes = int(value)
    except (TypeError, ValueError):
        return None
    if minutes < 0:
        return None
    return datetime.fromtimestamp(
        (minutes + KEEPA_EPOCH_OFFSET_MINUTES) * 60, tz=timezone.utc
    )


def _keepa_time_to_iso(value: Any) -> str | None:
    dt = _keepa_time_to_datetime(value)
    return dt.isoformat() if dt else None


def _offer_history(offer_csv: Any) -> list[tuple[datetime, int, int]]:
    if not isinstance(offer_csv, list):
        return []
    rows = []
    for index in range(0, len(offer_csv) - 2, 3):
        dt = _keepa_time_to_datetime(offer_csv[index])
        price = _money(offer_csv[index + 1])
        shipping = _money(offer_csv[index + 2])
        if dt is not None and price is not None and shipping is not None:
            rows.append((dt, price, shipping))
    return rows


def _history_median(
    rows: list[tuple[datetime, int, int]], *, days: int, now: datetime
) -> int | None:
    cutoff = now - timedelta(days=days)
    totals = [price + shipping for dt, price, shipping in rows if dt >= cutoff]
    return int(round(median(totals))) if totals else None


def _latest_prime_exclusive_price(offer: dict[str, Any]) -> int | None:
    csv = offer.get("primeExclCSV")
    if not isinstance(csv, list) or len(csv) < 2:
        return None
    return _money(csv[-1])


def _extract_product(payload: dict[str, Any]) -> dict[str, Any]:
    products = payload.get("products")
    if isinstance(products, list) and products and isinstance(products[0], dict):
        return products[0]
    # Stable normalized fixture/bridge shape remains supported for deterministic
    # tests and future provider adapters.
    product = payload.get("product")
    if isinstance(product, dict):
        return product
    return payload if isinstance(payload, dict) else {}


def _age_hours(timestamp: str | None, now: datetime) -> float | None:
    if not timestamp:
        return None
    try:
        seen = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return None
    if seen.tzinfo is None:
        seen = seen.replace(tzinfo=timezone.utc)
    return max(0.0, (now - seen.astimezone(timezone.utc)).total_seconds() / 3600)


def _confidence(
    *,
    identity_verified: bool,
    offer_last_seen_at: str | None,
    shipping_jpy: int | None,
    in_stock: bool,
    seller_known: bool,
    fulfillment_known: bool,
    condition_known: bool,
    history_30d_median_jpy: int | None,
    history_90d_median_jpy: int | None,
    now: datetime,
) -> tuple[int, dict[str, int]]:
    age = _age_hours(offer_last_seen_at, now)
    freshness = (
        15
        if age is not None and age <= 24
        else 8
        if age is not None and age <= 72
        else 0
    )
    components = {
        "identity": 20 if identity_verified else 0,
        "freshness": freshness,
        "shipping": 15 if shipping_jpy is not None else 0,
        "stock": 15 if in_stock else 0,
        "seller_fulfillment": (
            10 if seller_known and fulfillment_known else 5 if seller_known else 0
        ),
        "condition": 10 if condition_known else 0,
        "price_history": (
            15
            if history_30d_median_jpy is not None
            and history_90d_median_jpy is not None
            else 8
            if history_90d_median_jpy is not None
            else 0
        ),
    }
    return sum(components.values()), components


def _normalized_offer(
    offer: dict[str, Any], *, index: int, live_indices: set[int], now: datetime
) -> dict[str, Any] | None:
    """Normalize either raw Keepa offer-object or stable bridge offer shape."""
    if isinstance(offer.get("offerCSV"), list):
        history = _offer_history(offer.get("offerCSV"))
        if not history:
            return None
        _, price, shipping = history[-1]
        last_seen = _keepa_time_to_iso(offer.get("lastSeen"))
        condition = CONDITION_NAMES.get(int(offer.get("condition", 0)), "unknown")
        in_stock = bool(offer.get("isShippable", False)) and (
            index in live_indices if live_indices else True
        )
        return {
            "price_jpy": price,
            "shipping_jpy": shipping,
            "seller_id": offer.get("sellerId"),
            "is_amazon": bool(offer.get("isAmazon", False)),
            "is_fba": bool(offer.get("isFBA", False)),
            "is_warehouse_deal": bool(offer.get("isWarehouseDeal", False)),
            "prime_eligible": bool(offer.get("isPrime", False)),
            "prime_exclusive": bool(offer.get("isPrimeExcl", False)),
            "prime_exclusive_price_jpy": _latest_prime_exclusive_price(offer),
            "condition": condition,
            "last_seen_at": last_seen,
            "in_stock": in_stock,
            "history_30d_median_jpy": _history_median(history, days=30, now=now),
            "history_90d_median_jpy": _history_median(history, days=90, now=now),
        }

    price = _money(offer.get("price_jpy"))
    if price is None:
        return None
    return {
        "price_jpy": price,
        "shipping_jpy": _money(offer.get("shipping_jpy")),
        "seller_id": offer.get("seller_id"),
        "is_amazon": bool(offer.get("is_amazon", False)),
        "is_fba": bool(offer.get("is_fba", False)),
        "is_warehouse_deal": bool(offer.get("is_warehouse_deal", False)),
        "prime_eligible": offer.get("prime_eligible")
        if offer.get("prime_eligible") in (True, False, None)
        else None,
        "prime_exclusive": bool(offer.get("prime_exclusive", False)),
        "prime_exclusive_price_jpy": _money(
            offer.get("prime_exclusive_price_jpy")
        ),
        "condition": str(offer.get("condition") or "unknown"),
        "last_seen_at": offer.get("last_seen_at"),
        "in_stock": bool(offer.get("in_stock", False)),
        "history_30d_median_jpy": _money(offer.get("history_30d_median_jpy")),
        "history_90d_median_jpy": _money(offer.get("history_90d_median_jpy")),
    }


class AmazonKeepaObserver:
    name = "amazon_keepa_jp"

    def __init__(self, transport: Any | None = None):
        self.transport = transport or KeepaHttpTransport()

    def observe(
        self, asin: str, *, identity_verified: bool = False
    ) -> list[dict[str, Any]]:
        if not isinstance(asin, str) or not asin.strip():
            raise ValueError("asin is required")
        payload = self.transport.fetch_product(
            asin.strip(), domain=AMAZON_JP_KEEPA_DOMAIN
        )
        product = _extract_product(payload)
        title = str(product.get("title") or "")
        offers = product.get("offers", [])
        if not isinstance(offers, list):
            return []
        live = product.get("liveOffersOrder", [])
        live_indices = {
            int(value) for value in live if isinstance(value, int) and value >= 0
        } if isinstance(live, list) else set()

        now = datetime.now(timezone.utc)
        observed_at = now.isoformat()
        observations = []

        for index, raw_offer in enumerate(offers):
            if not isinstance(raw_offer, dict):
                continue
            offer = _normalized_offer(
                raw_offer, index=index, live_indices=live_indices, now=now
            )
            if offer is None:
                continue
            shipping = offer["shipping_jpy"]
            regular_total = (
                None
                if shipping is None
                else offer["price_jpy"] + shipping
            )
            prime_price = offer["prime_exclusive_price_jpy"]
            if (
                offer["prime_eligible"] is True
                and shipping is not None
            ):
                prime_total = (
                    (prime_price if prime_price is not None else offer["price_jpy"])
                    + shipping
                )
            else:
                prime_total = regular_total

            seller_id = offer["seller_id"]
            is_amazon = offer["is_amazon"]
            is_fba = offer["is_fba"]
            condition = offer["condition"]
            score, components = _confidence(
                identity_verified=identity_verified,
                offer_last_seen_at=offer["last_seen_at"],
                shipping_jpy=shipping,
                in_stock=offer["in_stock"],
                seller_known=bool(seller_id or is_amazon),
                fulfillment_known=is_amazon or is_fba,
                condition_known=condition != "unknown",
                history_30d_median_jpy=offer["history_30d_median_jpy"],
                history_90d_median_jpy=offer["history_90d_median_jpy"],
                now=now,
            )
            observation = AmazonSourceObservation(
                asin=asin.strip(),
                title=title,
                condition=condition,
                seller_id=str(seller_id) if seller_id is not None else None,
                is_amazon=is_amazon,
                is_fba=is_fba,
                is_warehouse_deal=offer["is_warehouse_deal"],
                prime_eligible=offer["prime_eligible"],
                prime_exclusive=offer["prime_exclusive"],
                price_jpy=offer["price_jpy"],
                prime_exclusive_price_jpy=prime_price,
                shipping_jpy=shipping,
                total_acquisition_non_prime_jpy=regular_total,
                total_acquisition_prime_jpy=prime_total,
                observed_at=observed_at,
                offer_last_seen_at=offer["last_seen_at"],
                history_30d_median_jpy=offer["history_30d_median_jpy"],
                history_90d_median_jpy=offer["history_90d_median_jpy"],
                source_confidence=score,
                confidence_components=components,
            )
            row = asdict(observation)
            row["source"] = self.name
            row["in_stock"] = offer["in_stock"]
            observations.append(row)
        return observations


def assess_amazon_source(
    observation: dict[str, Any],
    *,
    capital_jpy: int,
    conservative_sale_price_jpy: int,
    selling_fee_jpy: int,
    outbound_shipping_jpy: int,
    packing_jpy: int = 0,
    min_net_profit_jpy: int = 300,
    min_confidence: int = DEFAULT_MIN_CONFIDENCE,
    prime_member: bool = False,
) -> dict[str, Any]:
    """Read-only P2 source gate. Passing never authorizes a purchase."""
    total_key = (
        "total_acquisition_prime_jpy"
        if prime_member
        else "total_acquisition_non_prime_jpy"
    )
    total = _money(observation.get(total_key))
    confidence = int(observation.get("source_confidence") or 0)
    sale = _money(conservative_sale_price_jpy) or 0
    fee = _money(selling_fee_jpy) or 0
    outbound = _money(outbound_shipping_jpy) or 0
    packing = _money(packing_jpy) or 0
    capital = _money(capital_jpy)
    minimum = _money(min_net_profit_jpy)
    if capital is None or minimum is None:
        raise ValueError("capital_jpy and min_net_profit_jpy must be non-negative")

    if total is None:
        status, reason, net = (
            "rejected",
            "shipping_or_total_acquisition_unknown",
            None,
        )
    else:
        net = sale - fee - outbound - packing - total
        if observation.get("in_stock") is not True:
            status, reason = "rejected", "source_unavailable"
        elif total > capital:
            status, reason = "rejected", "over_capital"
        elif confidence < min_confidence:
            status, reason = (
                "rejected",
                "amazon_source_confidence_below_minimum",
            )
        elif net < minimum:
            status, reason = "rejected", "insufficient_margin"
        else:
            status, reason = "selection_eligible", "amazon_source_gate_passed"

    return {
        "version": OBSERVER_VERSION,
        "status": status,
        "reason": reason,
        "source": observation.get("source", "amazon_keepa_jp"),
        "asin": observation.get("asin"),
        "prime_member_scenario": bool(prime_member),
        "source_confidence": confidence,
        "total_acquisition_jpy": total,
        "conservative_sale_price_jpy": sale,
        "expected_net_profit_jpy": net,
        "min_net_profit_jpy": minimum,
        "capital_jpy": capital,
        "human_gate_required": True,
        "external_execution_authorized": False,
        "purchase_authorized": False,
    }
