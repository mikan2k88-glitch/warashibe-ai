from market_engine import find_items
from policy_engine import START_CAPITAL, evaluate_trade
from research_lab.repair_execution_controller import control_repair_execution


EXPECTED_START_CAPITAL = 3_000


def main():
    planned = control_repair_execution(
        state="plan",
        planning={
            "recurrence_result": {
                "status": "recurrence_not_contained",
                "guardrail_effective": False,
            },
            "repair_kind": "tighten_gate",
            "target": "product start capital policy",
            "rationale": "align the v1 product start amount with the approved initial capital",
            "path": "policy_engine.py",
            "change_summary": "set the product start capital to 3000 yen",
            "expected_test": "research_lab.test_product_start_capital",
        },
    )
    assert planned["controller_state"] == "write"
    assert planned["next_action"] == "execute_single_file_git_write"
    assert planned["execution_plan"]["path"] == "policy_engine.py"

    assert START_CAPITAL == EXPECTED_START_CAPITAL

    items = find_items(START_CAPITAL)
    assert items
    assert all(item["price"] == START_CAPITAL for item in items)
    assert all(evaluate_trade(START_CAPITAL, item)["allowed"] is True for item in items)

    repair = control_repair_execution(
        state="ci",
        write_evidence={
            "before_sha": "fed644480232c493f48ddf9e06ca197e55998076",
            "after_sha": "24ef74142c0e5ed651acf56a78a8e991469625b9",
            "path": "policy_engine.py",
            "expected_test": "research_lab.test_product_start_capital",
        },
        ci_evidence={
            "cycle_id": "product-gap-pg002-1044",
            "repair_id": "pg002-start-capital-3000",
            "observed_sha": "24ef74142c0e5ed651acf56a78a8e991469625b9",
            "ci_status": "completed",
            "ci_conclusion": "success",
        },
    )
    assert repair["status"] == "repair_pipeline_complete"
    assert repair["milestone_reached"] is True
    assert repair["next_action"] == "advance_problem_queue"
    assert repair["result"]["audit"]["status"] == "repair_audit_record_ready"
    assert repair["result"]["ledger"]["status"] == "repair_ledger_ready"


if __name__ == "__main__":
    main()
