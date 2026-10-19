"""Contract tests for the P2 v2.4 Amazon/Keepa sourcing observer."""

from datetime import datetime, timezone

from research_lab.amazon_keepa_observer import (
    KEEPA_EPOCH_OFFSET_MINUTES,
    AmazonKeepaObserver,
    assess_amazon_source,
)


def _keepa_now():
    return int(datetime.now(timezone.utc).timestamp() // 60) - KEEPA_EPOCH_OFFSET_MINUTES


class FakeKeepaTransport:
    def fetch_product(self, asin, *, domain):
        now = _keepa_now()
        return {
            "products": [
                {
                    "asin": asin,
                    "domainId": domain,
                    "title": "Warashibe Test Item",
                    "liveOffersOrder": [0, 1],
                    "offers": [
                        {
                            "offerId": 1,
                            "lastSeen": now,
                            "sellerId": "AMAZON_TEST",
                            "isPrime": True,
                            "isFBA": True,
                            "isShippable": True,
                            "isWarehouseDeal": False,
                            "isAmazon": True,
                            "isPrimeExcl": True,
                            "condition": 1,
                            "offerCSV": [
                                now - (20 * 24 * 60),
                                1600,
                                0,
                                now - (5 * 24 * 60),
                                1500,
                                0,
                                now,
                                1400,
                                0,
                            ],
                            "primeExclCSV": [now - 120, 1350, now, 1300],
                        },
                        {
                            "offerId": 2,
                            "lastSeen": now,
                            "sellerId": "MARKETPLACE_TEST",
                            "isPrime": False,
                            "isFBA": False,
                            "isShippable": True,
                            "isWarehouseDeal": False,
                            "isAmazon": False,
                            "isPrimeExcl": False,
                            "condition": 4,
                            "offerCSV": [now, 1000, 500],
                        },
                    ],
                }
            ]
        }


def run():
    observer = AmazonKeepaObserver(transport=FakeKeepaTransport())
    rows = observer.observe("B000TESTJP", identity_verified=True)

    assert len(rows) == 2

    amazon = rows[0]
    assert amazon["source"] == "amazon_keepa_jp"
    assert amazon["asin"] == "B000TESTJP"
    assert amazon["condition"] == "new"
    assert amazon["prime_eligible"] is True
    assert amazon["prime_exclusive"] is True
    assert amazon["prime_exclusive_price_jpy"] == 1300
    assert amazon["shipping_jpy"] == 0
    assert amazon["total_acquisition_non_prime_jpy"] == 1400
    assert amazon["total_acquisition_prime_jpy"] == 1300
    assert amazon["history_30d_median_jpy"] == 1500
    assert amazon["history_90d_median_jpy"] == 1500
    assert amazon["source_confidence"] == 100
    assert amazon["external_execution_authorized"] is False
    assert amazon["purchase_authorized"] is False

    eligible = assess_amazon_source(
        amazon,
        capital_jpy=3000,
        conservative_sale_price_jpy=2400,
        selling_fee_jpy=240,
        outbound_shipping_jpy=210,
        packing_jpy=50,
        min_net_profit_jpy=300,
        prime_member=True,
    )
    assert eligible["status"] == "selection_eligible"
    assert eligible["expected_net_profit_jpy"] == 600
    assert eligible["prime_member_scenario"] is True
    assert eligible["human_gate_required"] is True
    assert eligible["external_execution_authorized"] is False
    assert eligible["purchase_authorized"] is False

    marketplace = rows[1]
    assert marketplace["total_acquisition_non_prime_jpy"] == 1500
    rejected = assess_amazon_source(
        marketplace,
        capital_jpy=3000,
        conservative_sale_price_jpy=1800,
        selling_fee_jpy=180,
        outbound_shipping_jpy=210,
        min_net_profit_jpy=300,
    )
    assert rejected["status"] == "rejected"
    assert rejected["reason"] in {
        "amazon_source_confidence_below_minimum",
        "insufficient_margin",
    }

    unknown_shipping = dict(amazon)
    unknown_shipping["total_acquisition_non_prime_jpy"] = None
    blocked = assess_amazon_source(
        unknown_shipping,
        capital_jpy=3000,
        conservative_sale_price_jpy=5000,
        selling_fee_jpy=500,
        outbound_shipping_jpy=210,
    )
    assert blocked["status"] == "rejected"
    assert blocked["reason"] == "shipping_or_total_acquisition_unknown"

    # A passing source is still only research evidence, never purchase authority.
    assert eligible["status"] == "selection_eligible"
    assert eligible["human_gate_required"] is True


if __name__ == "__main__":
    run()
    print("AMAZON KEEPA OBSERVER V2.4: PASSED")
