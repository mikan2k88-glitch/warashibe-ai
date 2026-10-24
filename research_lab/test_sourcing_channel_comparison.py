"""Contract tests for P2 v2.5 sourcing-channel comparison."""

from research_lab.sourcing_channel_comparison import (
    amazon_observation_to_source_offer,
    compare_source_offers,
    normalize_source_offer,
)


IDENTITY = "GAME:TEST-JAN-001:LIMITED_USED_COMPLETE"


def source(channel, name, item, shipping, handling=0, confidence=80, **extra):
    row = {
        "identity_key": IDENTITY,
        "source_channel": channel,
        "source_name": name,
        "item_price_jpy": item,
        "inbound_shipping_jpy": shipping,
        "source_handling_fee_jpy": handling,
        "other_acquisition_cost_jpy": 0,
        "in_stock": True,
        "identity_verified": True,
        "condition_match": True,
        "source_confidence": confidence,
    }
    row.update(extra)
    return row


def run():
    # Sticker-price winner must lose when shipping/handling makes landed cost
    # worse. This is the core v2.5 requirement.
    surugaya = source(
        "surugaya",
        "Surugaya",
        1200,
        550,
        handling=240,
        confidence=88,
    )
    netoff = source(
        "netoff",
        "NETOFF",
        1500,
        0,
        confidence=86,
    )
    bookoff = source(
        "bookoff",
        "BOOKOFF",
        1350,
        220,
        confidence=90,
    )
    result = compare_source_offers(
        [surugaya, netoff, bookoff],
        capital_jpy=3000,
        max_total_acquisition_jpy=1800,
    )
    assert result["status"] == "comparison_ready"
    assert result["source_offer_count"] == 3
    assert result["eligible_source_count"] == 2
    assert result["best_source"]["source_name"] == "NETOFF"
    assert result["best_source"]["total_acquisition_jpy"] == 1500
    assert result["human_gate_required"] is True
    assert result["purchase_authorized"] is False
    rejected = {row["source_name"]: row["reason"] for row in result["rejected_sources"]}
    assert rejected["Surugaya"] == "insufficient_margin"

    # Unknown inbound shipping is never treated as zero.
    unknown_shipping = source(
        "hardoff",
        "HardOff",
        900,
        None,
        confidence=85,
    )
    normalized = normalize_source_offer(unknown_shipping)
    assert normalized.total_acquisition_jpy is None
    blocked = compare_source_offers(
        [unknown_shipping],
        capital_jpy=3000,
        max_total_acquisition_jpy=2000,
    )
    assert blocked["status"] == "no_eligible_source"
    assert blocked["rejected_sources"][0]["reason"] == "shipping_loss"

    # Identity/condition integrity remains above nominal price.
    mismatch = source(
        "mercari_shops",
        "Mercari Shops",
        500,
        0,
        confidence=95,
        condition_match=False,
    )
    mismatch_result = compare_source_offers(
        [mismatch],
        capital_jpy=3000,
        max_total_acquisition_jpy=2000,
    )
    assert mismatch_result["rejected_sources"][0]["reason"] == "condition_mismatch"

    # Amazon remains a pluggable source while Keepa live access is deferred.
    amazon = amazon_observation_to_source_offer(
        {
            "asin": "B000V25TEST",
            "price_jpy": 1400,
            "shipping_jpy": 0,
            "total_acquisition_non_prime_jpy": 1400,
            "total_acquisition_prime_jpy": 1300,
            "source_confidence": 92,
            "in_stock": True,
            "observed_at": "2026-10-20T00:00:00+00:00",
        },
        identity_key=IDENTITY,
        prime_member=True,
    )
    assert amazon.source_channel == "amazon_keepa_jp"
    assert amazon.total_acquisition_jpy == 1300

    with_amazon = compare_source_offers(
        [netoff, amazon],
        capital_jpy=3000,
        max_total_acquisition_jpy=1800,
    )
    assert with_amazon["best_source"]["source_channel"] == "amazon_keepa_jp"
    assert with_amazon["best_source"]["total_acquisition_jpy"] == 1300
    assert with_amazon["external_execution_authorized"] is False
    assert with_amazon["purchase_authorized"] is False

    # Cross-product comparison is forbidden.
    wrong_identity = dict(netoff)
    wrong_identity["identity_key"] = "GAME:OTHER"
    try:
        compare_source_offers([netoff, wrong_identity], capital_jpy=3000)
    except ValueError as exc:
        assert "same identity_key" in str(exc)
    else:
        raise AssertionError("identity mismatch must fail closed")


if __name__ == "__main__":
    run()
    print("P2 V2.5 SOURCING CHANNEL COMPARISON: PASSED")
