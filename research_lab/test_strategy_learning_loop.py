"""Strategy Learning Loop contract tests."""

from research_lab.strategy_learning_loop import run_strategy_learning_loop
from copy import deepcopy
from research_lab.strategy_learning_loop import build_strategy_learning_proposal, validate_strategy_learning_proposal, decide_strategy_learning_update


def main():
    result = run_strategy_learning_loop(
        as_of="2026-10-04T00:00:00Z",
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
        as_of="2026-10-04T00:00:00Z",
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

    findings = deepcopy(result['proposal']['findings'])
    for bad in (float('nan'), float('inf'), -float('inf'), True, -1):
        bad_result = run_strategy_learning_loop(findings=findings,
            proposed_rule_updates={'target_net_profit_jpy_min': bad}, rationale='fixture',
            as_of='2026-10-04T00:00:00Z')
        assert bad_result['decision']['decision'] == 'reject'
    for timestamp in ('not-a-date', '2020-01-01', '2026-10-05', '2026-10-03T00:00:00'):
        changed = deepcopy(findings)
        changed[0]['observed_at'] = timestamp
        bad_result = run_strategy_learning_loop(findings=changed,
            proposed_rule_updates={'target_net_profit_jpy_min': 300}, rationale='fixture',
            as_of='2026-10-04T00:00:00Z')
        assert bad_result['decision']['decision'] == 'reject', timestamp
    changed = deepcopy(findings)
    changed[0]['source_url'] = 'https://EXAMPLE.com/item/?utm_source=a'
    changed[1]['source_url'] = 'https://example.com/item?utm_source=b#fragment'
    duplicate = run_strategy_learning_loop(findings=changed,
        proposed_rule_updates={'target_net_profit_jpy_min': 300}, rationale='fixture',
        as_of='2026-10-04T00:00:00Z')
    assert duplicate['validation']['distinct_source_count'] == 1
    assert duplicate['decision']['decision'] == 'reject'
    proposal = deepcopy(result['proposal'])
    proposal['proposed_rule_updates']['target_net_profit_jpy_min'] = 999
    assert decide_strategy_learning_update(proposal, result['validation'])['decision'] == 'reject'
    forged = deepcopy(result['validation'])
    forged.pop('validated_proposal')
    assert decide_strategy_learning_update(result['proposal'], forged)['decision'] == 'reject'
    altered = deepcopy(result['proposal'])
    altered['proposed_rule_updates']['unknown'] = 10
    try:
        validate_strategy_learning_proposal(altered)
        raise AssertionError('unknown rule accepted')
    except ValueError:
        pass

    print("Strategy Learning Loop tests passed")


if __name__ == "__main__":
    main()
