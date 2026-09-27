"""Deterministic end-to-end market decision pipeline check."""

from research_lab.end_to_end_market_decision_pipeline import run_market_decision
from research_lab.market_decision_virtual_trade import simulate_decision_trade


class FixtureProvider:
    name = "fixture-market"

    def fetch(self, query):
        assert query == "camera"
        base = {
            "name": "Camera A", "category": "camera", "currency": "JPY",
            "purchase_price": 10000, "expected_sale_price": 14000,
            "sale_probability": .75, "confidence": .8, "evidence_count": 2,
            "estimated_days_to_sale": 3, "recovery_value": 7000,
            "metadata": {"gtin": "09521234000006", "model_number": "CAM-A"},
        }
        rows = []
        for source, price in (("market-a", 10000), ("market-b", 10500)):
            row = dict(base)
            row.update({"external_id": source, "source": source, "purchase_price": price})
            rows.append(row)
        return rows


def main():
    run = run_market_decision(
        FixtureProvider(), "camera", 11000,
        min_confidence=.5, min_evidence_count=3, min_source_count=2,
    )
    assert run.raw_count == 2
    assert run.normalized_count == 2
    assert run.estimate_count == 1
    assert run.decision["quality_accepted"] == 1
    assert run.decision["quality_rejected"] == 0
    assert run.decision["input_estimates"] == 1
    class MixedProvider(FixtureProvider):
        def fetch(self, query):
            rows = super().fetch(query)
            return [rows[0], None, {**rows[0], "metadata": []}, rows[1],
                    {**rows[0], "purchase_price": 10 ** 1000}]

    mixed = run_market_decision(
        MixedProvider(), " camera ", 11000,
        min_confidence=.5, min_evidence_count=3, min_source_count=2,
    )
    assert mixed.provider == "fixture-market"
    assert mixed.query == "camera"
    assert mixed.raw_count == 5
    assert mixed.normalized_count == 2
    assert mixed.normalization_rejected == 3
    assert mixed.estimate_count == 1
    assert mixed.decision["quality_accepted"] == 1
    assert mixed.decision["quality_rejected"] == 0
    assert mixed.decision["input_estimates"] == 1

    # One-item decision is a proposal, not a purchase or a capital mutation.
    selected = mixed.decision["best_candidate"]
    assert selected is not None
    assert selected["name"] == "Camera A"
    assert selected["purchase_price"] <= 11000
    assert selected["rank"] == 1
    assert len(mixed.decision["ranked_candidates"]) == 1
    assert mixed.decision["current_capital"] == 11000

    unaffordable = run_market_decision(
        MixedProvider(), "camera", 9000,
        min_confidence=.5, min_evidence_count=3, min_source_count=2,
    )
    assert unaffordable.normalized_count == 2
    assert unaffordable.decision["quality_accepted"] == 1
    assert unaffordable.decision["best_candidate"] is None
    assert unaffordable.decision["capital_allowed_count"] == 0
    assert unaffordable.decision["capital_blocked_count"] == 1
    assert unaffordable.decision["current_capital"] == 9000

    # Deterministic virtual transition: exactly one candidate, no external action.
    before = dict(mixed.decision)
    won = simulate_decision_trade(mixed.decision, 0.0)
    lost = simulate_decision_trade(mixed.decision, 0.99)
    assert won["status"] == "success" and won["capital_after"] == selected["expected_sale_price"]
    assert lost["status"] == "failed" and lost["capital_after"] == 0
    assert won["capital_before"] == lost["capital_before"] == 11000
    assert won["selected_item"] == lost["selected_item"] == "Camera A"
    assert not won["external_action_authorized"] and not lost["external_action_authorized"]
    assert mixed.decision == before
    stopped = simulate_decision_trade(unaffordable.decision, 0.0)
    assert stopped["status"] == "no_candidate" and stopped["capital_after"] == 9000
    for invalid_draw in (-0.1, 1, float("nan"), True):
        try:
            simulate_decision_trade(mixed.decision, invalid_draw)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid draw accepted")

    print("end-to-end market decision pipeline tests passed")


if __name__ == "__main__":
    main()
