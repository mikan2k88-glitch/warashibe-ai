from capital_filter import evaluate_capital_fit
from research_lab.repair_execution_controller import control_repair_execution


def main():
    planned = control_repair_execution(
        state="plan",
        planning={
            "recurrence_result": {
                "status": "recurrence_not_contained",
                "guardrail_effective": False,
            },
            "repair_kind": "tighten_gate",
            "target": "capital filter product policy",
            "rationale": "align candidate capital rule with the product policy",
            "path": "capital_filter.py",
            "change_summary": "require exact full-capital fit for one candidate",
            "expected_test": "research_lab.test_product_capital_policy",
        },
    )
    assert planned["controller_state"] == "write"
    assert planned["next_action"] == "execute_single_file_git_write"
    assert planned["execution_plan"]["path"] == "capital_filter.py"

    # PG-006 targeted RED: candidate selection must expose one common
    # selection record that can be persisted/audited by later product stages.
    from candidate_engine import create_candidate
    from candidate_pipeline import evaluate_candidates

    candidate = create_candidate(
        name="PG-006 exact-capital candidate",
        purchase_price=10_000,
        expected_sale_price=12_000,
        source="product_test",
        category="book",
        confidence=0.9,
        success_probability=0.8,
    )
    selection = evaluate_candidates([candidate], 10_000)
    record = selection["selection_record"]
    assert record["selected_candidate"] == selection["best_candidate"]
    assert record["selection_reason"]
    assert record["strategy_result"] is not None
    assert "simulation_result" in record

    exact = evaluate_capital_fit(
        10_000,
        {"purchase_price": 10_000},
    )
    assert exact["allowed"] is True

    under = evaluate_capital_fit(
        10_000,
        {"purchase_price": 8_000},
    )
    assert under["allowed"] is False
    assert under["capital_usage_rate"] == 0.8
    assert under["reasons"]

    over = evaluate_capital_fit(
        10_000,
        {"purchase_price": 12_000},
    )
    assert over["allowed"] is False

    zero = evaluate_capital_fit(
        10_000,
        {"purchase_price": 0},
    )
    assert zero["allowed"] is False

    repair = control_repair_execution(
        state="ci",
        write_evidence={
            "before_sha": "f395cf00c46106f69a36bb02ce82d354d1962bc3",
            "after_sha": "8f4480fe46c2737ac28d8e5873ed6f54c0b145d8",
            "path": "capital_filter.py",
            "expected_test": "research_lab.test_product_capital_policy",
        },
        ci_evidence={
            "cycle_id": "product-gap-pg001-1035",
            "repair_id": "pg001-full-capital-policy",
            "observed_sha": "8f4480fe46c2737ac28d8e5873ed6f54c0b145d8",
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
