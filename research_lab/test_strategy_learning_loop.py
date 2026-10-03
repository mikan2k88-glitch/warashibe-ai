"""Strategy Learning Loop contract tests."""

from research_lab.strategy_learning_loop import run_strategy_learning_loop


def main():
    result = run_strategy_learning_loop(
        findings=[
            {
                "topic": "shipping_cost",
                "source_url": "https://example.com/source-a",
                "observed_at": "2026-10-03",
                "evidence": {"shipping_jpy": 600},
            },
            {
                "topic": "market_price_spread",
                "source_url": "https://example.org/source-b",
                "observed_at": "2026-10-03",
                "evidence": {"sale_price_jpy": 2500, "acquisition_jpy": 1940},
            },
        ],
        proposed_rule_updates={
            "target_total_acquisition_cost_jpy_max": 2200,
            "target_net_profit_jpy_min": 300,
        },
        rationale="送料負けを避け、P2で最低利益を確保する。",
    )
    assert result["status"] == "strategy_learning_loop_complete"
    assert result["validation"]["valid"] is True
    assert result["decision"]["decision"] == "adopt_for_p2_evaluation"
    assert result["decision"]["requires_shadow_validation"] is True
    assert result["production_rule_changed"] is False
    assert result["external_execution_authorized"] is False

    rejected = run_strategy_learning_loop(
        findings=[
            {
                "topic": "selling_fee",
                "source_url": "https://example.com/one-source",
                "observed_at": "2026-10-03",
                "evidence": {"fee_rate": 0.10},
            }
        ],
        proposed_rule_updates={"target_net_profit_jpy_min": 350},
        rationale="単一情報源だけでは本番ルールを変えない。",
    )
    assert rejected["validation"]["valid"] is False
    assert rejected["decision"]["decision"] == "reject"
    assert rejected["next_action"] == "collect_more_evidence"

    print("Strategy Learning Loop tests passed")


if __name__ == "__main__":
    main()
