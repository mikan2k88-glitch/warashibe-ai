"""Offline, reproducible one-item decision explanation using the existing scorer."""

from research_lab.real_world_candidate_scoring_design import rank_candidates, score_candidate


def explain_one_item(candidates, capital):
    """Explain an illustrative choice; never authorize commerce."""
    if not isinstance(capital, (int, float)) or isinstance(capital, bool) or capital <= 0:
        raise ValueError("invalid_capital")
    rows = []
    for item in candidates:
        result = score_candidate(item)
        affordable = (
            result.get("valid") is True
            and item["purchase_price_jpy"] + item["estimated_fees_jpy"]
            + item["estimated_shipping_jpy"] <= capital
        )
        rows.append({
            "name": item.get("name"),
            "affordable": affordable,
            "scoring": result,
            "reason": "invalid_candidate" if not result.get("valid") else (
                "exceeds_capital" if not affordable else (
                    "policy_blocked" if not result["eligible"] else "eligible"
                )
            ),
        })
    allowed = [item for item, row in zip(candidates, rows) if row["reason"] == "eligible"]
    ranked = rank_candidates(allowed)
    chosen = ranked[0] if ranked else None
    return {
        "capital_jpy": capital,
        "evaluated": rows,
        "selected_name": chosen.get("name") if chosen else None,
        "selection_reason": "highest_existing_loss_adjusted_score" if chosen else "no_eligible_item",
        "one_item_only": True,
        "scenario_only": True,
        "purchase_authorized": False,
        "external_action_authorized": False,
    }


def test_explanation():
    base = {
        "purchase_price_jpy": 100, "estimated_sale_price_jpy": 180,
        "estimated_fees_jpy": 10, "estimated_shipping_jpy": 10,
        "estimated_days_to_sell": 4, "liquidation_value_jpy": 100,
        "market_depth": 0.8, "automation_ease": 0.8, "confidence": 0.8,
    }
    quick = dict(base, name="quick")
    slow = dict(base, name="slow", estimated_days_to_sell=10)
    unaffordable = dict(base, name="unaffordable", purchase_price_jpy=150)
    loss = dict(base, name="loss", estimated_sale_price_jpy=90)
    report = explain_one_item([slow, quick, unaffordable, loss], 120)
    assert report["selected_name"] == "quick"
    assert report["one_item_only"] and not report["purchase_authorized"]
    assert [r["reason"] for r in report["evaluated"]] == [
        "eligible", "eligible", "exceeds_capital", "policy_blocked"
    ]
    assert report["evaluated"][1]["scoring"]["expected_net_profit_jpy"] == 60
    assert report["evaluated"][1]["scoring"]["maximum_expected_loss_jpy"] == 20
    assert report["evaluated"][1]["scoring"]["profit_per_day_jpy"] == 15
    assert explain_one_item([unaffordable], 120)["selected_name"] is None
    try:
        explain_one_item([quick], 0)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid capital accepted")


if __name__ == "__main__":
    test_explanation()
    print("PASS: offline one-item decision explanation")
