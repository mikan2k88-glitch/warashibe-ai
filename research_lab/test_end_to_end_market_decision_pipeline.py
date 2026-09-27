"""Deterministic end-to-end market decision pipeline check."""

from research_lab.end_to_end_market_decision_pipeline import run_market_decision
from research_lab.market_decision_virtual_trade import simulate_decision_trade
from research_lab.market_decision_virtual_journey import run_virtual_journey
from research_lab.market_decision_virtual_statistics import evaluate_virtual_journeys
from research_lab.market_decision_virtual_campaign import run_virtual_campaign
from research_lab.virtual_trade_costs import apply_virtual_trade_costs


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

    # Multiple steps: fresh fixture evidence at each capital, one item per step.
    calls = []

    class StepProvider:
        name = "fixture-market"

        def __init__(self, capital):
            self.capital = capital

        def fetch(self, query):
            assert query == "camera"
            price = self.capital * 0.8
            return [{
                "external_id": source, "name": "Camera A", "category": "camera",
                "source": source, "currency": "JPY", "purchase_price": price,
                "expected_sale_price": self.capital * 1.2,
                "sale_probability": 0.75, "confidence": 0.8,
                "evidence_count": 2, "recovery_value": self.capital * 0.5,
                "metadata": {"gtin": "09521234000006", "model_number": "CAM-A"},
            } for source in ("market-a", "market-b")]

    def provider_factory(step, capital):
        calls.append((step, capital))
        return StepProvider(capital)

    gates = dict(min_confidence=.5, min_evidence_count=3, min_source_count=2)
    journey = run_virtual_journey(provider_factory, "camera", 10000,
                                  (0.0, 0.0, 0.0), target=14000, max_steps=3, **gates)
    assert journey["status"] == "goal_reached" and journey["steps"] == 2
    assert calls == [(1, 10000), (2, 12000)]
    assert [row["capital_after"] for row in journey["history"]] == [12000, 14400]
    assert all(row["selected_item"] == "Camera A" for row in journey["history"])
    assert not journey["external_action_authorized"]

    calls.clear()
    failed = run_virtual_journey(provider_factory, "camera", 10000,
                                 (0.0, .99, 0.0), target=20000, max_steps=3, **gates)
    assert failed["status"] == "failed" and failed["final_capital"] == 0
    assert failed["steps"] == 2 and len(calls) == 2
    calls.clear()
    capped = run_virtual_journey(provider_factory, "camera", 10000,
                                 (0.0, 0.0), target=20000, max_steps=2, **gates)
    assert capped["status"] == "max_steps_reached" and capped["final_capital"] == 14400
    calls.clear()
    no_candidate = run_virtual_journey(provider_factory, "camera", 10000,
                                       (0.0,), target=20000, max_steps=1,
                                       min_confidence=.5, min_evidence_count=3, min_source_count=3)
    assert no_candidate["status"] == "no_candidate" and no_candidate["final_capital"] == 10000
    assert no_candidate["steps"] == 1
    calls.clear()
    try:
        run_virtual_journey(provider_factory, "camera", 10000, (float("nan"),), max_steps=1)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid draw accepted")
    assert calls == []

    # Seeded statistics use the same bounded, one-item fixture journey.
    def stats(**kwargs):
        return evaluate_virtual_journeys(provider_factory, "camera", 10000,
            trials=40, seed=17, target=14000, max_steps=3, **gates, **kwargs)

    first = stats()
    assert first == stats()
    assert first["trials"] == 40 and first["seed"] == 17
    assert sum(first["status_counts"].values()) == 40
    assert set(first["status_counts"]) == {
        "goal_reached", "failed", "no_candidate", "max_steps_reached"
    }
    assert first["status_counts"]["goal_reached"] + first["status_counts"]["failed"] == 40
    assert first["goal_rate_percent"] == 100 * first["status_counts"]["goal_reached"] / 40
    assert 1 <= first["average_steps"] <= 2
    assert first["average_max_capital"] >= first["average_final_capital"]
    assert not first["external_action_authorized"]
    for bad in (0, -1, True, 10001):
        try:
            evaluate_virtual_journeys(provider_factory, "camera", 10000, trials=bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid trials accepted")

    # Agreed baseline: 3,000 JPY start, 1,000,000 JPY goal.
    # With this illustrative +20% gross-sale fixture and a 20-step cap,
    # even an all-success route does not reach the goal.
    baseline = run_virtual_journey(provider_factory, "camera", 3000,
        (0.0,) * 20, target=1_000_000, max_steps=20, **gates)
    assert baseline["start_capital"] == 3000 and baseline["target"] == 1_000_000
    assert baseline["status"] == "max_steps_reached" and baseline["steps"] == 20
    assert 3000 < baseline["final_capital"] < 1_000_000
    baseline_stats = evaluate_virtual_journeys(provider_factory, "camera", 3000,
        trials=40, seed=17, target=1_000_000, max_steps=20, **gates)
    assert baseline_stats["start_capital"] == 3000
    assert baseline_stats["target"] == 1_000_000
    assert baseline_stats["status_counts"]["goal_reached"] == 0
    assert baseline_stats["goal_rate_percent"] == 0
    assert sum(baseline_stats["status_counts"].values()) == 40
    assert baseline_stats == evaluate_virtual_journeys(provider_factory, "camera", 3000,
        trials=40, seed=17, target=1_000_000, max_steps=20, **gates)

    # Full loss starts a NEW attempt with 3,000 JPY, not a capital injection.
    calls.clear()
    campaign = run_virtual_campaign(provider_factory, "camera",
        ((.99,), (0.0,)), target=3500, max_steps=1, **gates)
    assert campaign["attempt_count"] == 2 and campaign["restart_count"] == 1
    assert [a["start_capital"] for a in campaign["attempts"]] == [3000, 3000]
    assert [a["final_capital"] for a in campaign["attempts"]] == [0, 3600]
    assert campaign["status"] == "goal_reached" and campaign["final_capital"] == 3600
    assert calls == [(1, 3000), (1, 3000)]
    assert not campaign["external_action_authorized"]
    calls.clear()
    stop = run_virtual_campaign(provider_factory, "camera",
        ((0.0,), (.99,)), target=3500, max_steps=1, **gates)
    assert stop["attempt_count"] == 1 and stop["restart_count"] == 0
    assert calls == [(1, 3000)]
    for bad in (0, 100, True):
        try:
            run_virtual_campaign(provider_factory, "camera", ((0.0,),),
                                 restart_capital=bad, max_steps=1)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid restart capital accepted")

    # Opt-in salvage retains a positive balance within the SAME attempt.
    calls.clear()
    salvaged = run_virtual_campaign(provider_factory, "camera",
        ((.99, 0.0), (0.0, 0.0)), target=3500, max_steps=2,
        salvage_on_failure=True, **gates)
    assert salvaged["attempt_count"] == 1 and salvaged["restart_count"] == 0
    assert calls == [(1, 3000), (2, 1500)]
    history = salvaged["attempts"][0]["history"]
    assert history[0]["status"] == "salvaged" and history[0]["capital_after"] == 1500
    assert history[1]["capital_before"] == 1500 and history[1]["status"] == "success"
    assert salvaged["final_capital"] == 1800
    assert salvaged["status"] == "max_steps_reached"
    assert not salvaged["external_action_authorized"]
    # Without opt-in, the same failed sale remains a full loss and restarts.
    calls.clear()
    default = run_virtual_campaign(provider_factory, "camera",
        ((.99, 0.0), (0.0, 0.0)), target=3500, max_steps=2, **gates)
    assert default["attempt_count"] == 2 and default["restart_count"] == 1
    assert default["attempts"][0]["final_capital"] == 0
    # Invalid recovery must fail closed, never mint additional capital.
    malformed = {"current_capital": 3000, "best_candidate": {
        "name": "bad", "purchase_price": 2400, "expected_sale_price": 3600,
        "confidence": .8, "metadata": {"recovery_value": 4000}}}
    try:
        simulate_decision_trade(malformed, .99, salvage_on_failure=True)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid recovery accepted")

    # Optional cash ledger: keep unspent cash, charge hypothetical fees once.
    cost_decision = {"current_capital": 3000, "best_candidate": {
        "name": "Camera A", "purchase_price": 2400,
        "expected_sale_price": 3600, "confidence": .8,
        "metadata": {"recovery_value": 1500}}}
    gross_win = simulate_decision_trade(cost_decision, 0.0)
    net_win = apply_virtual_trade_costs(gross_win, inbound_shipping=100,
        outbound_shipping=200, selling_fee_rate=.1)
    assert net_win["unspent_cash"] == 500
    assert net_win["selling_fee"] == 360 and net_win["total_costs"] == 660
    assert net_win["capital_after"] == 3540 and net_win["cost_model"] == "cash_ledger"
    assert gross_win["capital_after"] == 3600  # Legacy gross model unchanged.
    recovered = simulate_decision_trade(cost_decision, .99, salvage_on_failure=True)
    net_recovered = apply_virtual_trade_costs(recovered, inbound_shipping=100,
        outbound_shipping=200, selling_fee_rate=.1)
    assert net_recovered["capital_after"] == 1650  # 500 + 1500 - 150 - 200
    zero_sale = simulate_decision_trade(cost_decision, .99)
    net_zero = apply_virtual_trade_costs(zero_sale, inbound_shipping=100,
        outbound_shipping=200, selling_fee_rate=.1)
    assert net_zero["status"] == "salvaged" and net_zero["capital_after"] == 500
    assert net_zero["outbound_shipping"] == 0
    for costs in ({"inbound_shipping": 601}, {"selling_fee_rate": 1.1},
                  {"outbound_shipping": 4000}, {"inbound_shipping": True}):
        try:
            apply_virtual_trade_costs(gross_win, **costs)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid virtual costs accepted")

    # Cash ledger is applied at EVERY step before the next provider fetch.
    fees = dict(inbound_shipping=100, outbound_shipping=200, selling_fee_rate=.1)
    calls.clear()
    net_journey = run_virtual_journey(provider_factory, "camera", 3000,
        (0.0, 0.0), target=1_000_000, max_steps=2, cost_kwargs=fees, **gates)
    assert net_journey["status"] == "max_steps_reached"
    assert net_journey["history"][0]["capital_after"] == 3540
    assert calls == [(1, 3000), (2, 3540)]
    assert all(row["cost_model"] == "cash_ledger" for row in net_journey["history"])
    calls.clear()
    net_stats = evaluate_virtual_journeys(provider_factory, "camera", 3000,
        trials=40, seed=17, target=1_000_000, max_steps=2,
        cost_kwargs=fees, **gates)
    assert net_stats == evaluate_virtual_journeys(provider_factory, "camera", 3000,
        trials=40, seed=17, target=1_000_000, max_steps=2,
        cost_kwargs=fees, **gates)
    assert net_stats["start_capital"] == 3000 and net_stats["goal_rate_percent"] == 0
    assert sum(net_stats["status_counts"].values()) == 40
    assert net_stats["average_final_capital"] >= 0
    assert not net_stats["external_action_authorized"]
    # Legacy gross route remains available when the ledger is not requested.
    gross_journey = run_virtual_journey(provider_factory, "camera", 3000,
        (0.0, 0.0), target=1_000_000, max_steps=2, **gates)
    assert gross_journey["history"][0]["capital_after"] == 3600
    assert "cost_model" not in gross_journey["history"][0]

    print("end-to-end market decision pipeline tests passed")


if __name__ == "__main__":
    main()
