"""Read-only Amazon.co.jp sourcing observer backed by Keepa-compatible data.

P2 v2.4 boundary:
- observes and normalizes Amazon offers only;
- never buys, carts, lists, pays, or changes an account;
- keeps Prime/non-Prime economics separate;
- requires explicit shipping data instead of assuming "Prime == free";
- supports dependency-injected transport so CI is deterministic and secret-free.

The default transport uses KEEPA_API_KEY only when an operator explicitly calls it.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

OBSERVER_VERSION = "2.4"
AMAZON_JP_KEEPA_DOMAIN = 5
DEFAULT_MIN_CONFIDENCE = 70


@dataclass(frozen=True)
class AmazonSourceObservation:
    asin: str
    title: str
    condition: str
    seller_id: str | None
    seller_name: str | None
    is_amazon: bool
    is_fba: bool
    prime_eligible: bool | None
    price_jpy: int
    shipping_jpy: int | None
    total_acquisition_jpy: int | None
    observed_at: str
    offer_last_seen_at: str | None
    history_30d_median_jpy: int | None
    history_90d_median_jpy: int | None
    source_confidence: int
    confidence_components: dict[str, int]
    external_execution_authorized: bool = False
    purchase_authorized: bool = False


class KeepaHttpTransport:
    """Minimal read-only Keepa transport.

    It intentionally exposes only GET. The API key is read at call time and is
    never included in returned observations.
    """

    endpoint = "https://api.keepa.com/product"

    def __init__(self, api_key: str | None = None, timeout_seconds: int = 20):
        self._api_key = api_key
        self.timeout_seconds = timeout_seconds

    def fetch_product(self, asin: str, *, domain: int = AMAZON_JP_KEEPA_DOMAIN) -> dict[str, Any]:
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
        url = f"{self.endpoint}?{urlencode(params)}"
        with urlopen(url, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))


def _money(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        parsed = int(round(float(value)))
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
    freshness = 15 if age is not None and age <= 24 else 8 if age is not None and age <= 72 else 0
    components = {
        "identity": 20 if identity_verified else 0,
        "freshness": freshness,
        "shipping": 15 if shipping_jpy is not None else 0,
        "stock": 15 if in_stock else 0,
        "seller_fulfillment": 10 if seller_known and fulfillment_known else 5 if seller_known else 0,
        "condition": 10 if condition_known else 0,
        "price_history": 15 if history_30d_median_jpy is not None and history_90d_median_jpy is not None else 8 if history_90d_median_jpy is not None else 0,
    }
    return sum(components.values()), components


def _normalized_offer_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Accept the normalized Keepa bridge shape used by Warashibe.

    A future Keepa raw-payload adapter can map Keepa's compact offer structures
    into this stable shape without changing the selection/economics layer.
    """
    rows = payload.get("offers", [])
    return rows if isinstance(rows, list) else []


class AmazonKeepaObserver:
    name = "amazon_keepa_jp"

    def __init__(self, transport: Any | None = None):
        self.transport = transport or KeepaHttpTransport()

    def observe(self, asin: str, *, identity_verified: bool = False) -> list[dict[str, Any]]:
        if not isinstance(asin, str) or not asin.strip():
            raise ValueError("asin is required")
        payload = self.transport.fetch_product(asin.strip(), domain=AMAZON_JP_KEEPA_DOMAIN)
        product = payload.get("product") if isinstance(payload.get("product"), dict) else payload
        title = str(product.get("title") or "")
        history = product.get("history", {}) if isinstance(product.get("history"), dict) else {}
        h30 = _money(history.get("median_30d_jpy"))
        h90 = _money(history.get("median_90d_jpy"))
        now = datetime.now(timezone.utc)
        observed_at = now.isoformat()

        observations = []
        for offer in _normalized_offer_rows(product):
            if not isinstance(offer, dict):
                continue
            price = _money(offer.get("price_jpy"))
            if price is None:
                continue
            shipping = _money(offer.get("shipping_jpy"))
            in_stock = bool(offer.get("in_stock", False))
            seller_id = offer.get("seller_id")
            seller_name = offer.get("seller_name")
            is_amazon = bool(offer.get("is_amazon", False))
            is_fba = bool(offer.get("is_fba", False))
            prime = offer.get("prime_eligible")
            if prime not in (True, False, None):
                prime = None
            condition = str(offer.get("condition") or "unknown")
            last_seen = offer.get("last_seen_at")
            score, components = _confidence(
                identity_verified=identity_verified,
                offer_last_seen_at=last_seen,
                shipping_jpy=shipping,
                in_stock=in_stock,
                seller_known=bool(seller_id or seller_name or is_amazon),
                fulfillment_known=is_amazon or is_fba or offer.get("fulfillment_known") is True,
                condition_known=condition != "unknown",
                history_30d_median_jpy=h30,
                history_90d_median_jpy=h90,
                now=now,
            )
            total = None if shipping is None else price + shipping
            observation = AmazonSourceObservation(
                asin=asin.strip(),
                title=title,
                condition=condition,
                seller_id=str(seller_id) if seller_id is not None else None,
                seller_name=str(seller_name) if seller_name is not None else None,
                is_amazon=is_amazon,
                is_fba=is_fba,
                prime_eligible=prime,
                price_jpy=price,
                shipping_jpy=shipping,
                total_acquisition_jpy=total,
                observed_at=observed_at,
                offer_last_seen_at=str(last_seen) if last_seen else None,
                history_30d_median_jpy=h30,
                history_90d_median_jpy=h90,
                source_confidence=score,
                confidence_components=components,
            )
            row = asdict(observation)
            row["source"] = self.name
            row["in_stock"] = in_stock
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
) -> dict[str, Any]:
    """Read-only P2 source gate. Never authorizes a purchase."""
    total = _money(observation.get("total_acquisition_jpy"))
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
        status, reason, net = "rejected", "shipping_or_total_acquisition_unknown", None
    else:
        net = sale - fee - outbound - packing - total
        if observation.get("in_stock") is not True:
            status, reason = "rejected", "source_unavailable"
        elif total > capital:
            status, reason = "rejected", "over_capital"
        elif confidence < min_confidence:
            status, reason = "rejected", "amazon_source_confidence_below_minimum"
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
