from capital_filter import evaluate_capital_fit
from policy_engine import POLICY_VERSION, evaluate_trade
from research_lab.repair_execution_controller import control_repair_execution


def _candidate(price):
    return {
        "name": "PG-003 candidate",
        "purchase_price": price,
        "expected_sale_price": 15_000,
        "confidence": 0.9,
    }


def _legacy(candidate):
    return {
        "name": candidate["name"],
        "price": candidate["purchase_price"],
        "next_value": candidate["expected_sale_price"],
        "success_rate": candidate["confidence"],
    }


def main():
    planned = control_repair_execution(
        state="plan",
        planning={
            "recurrence_result": {
                "status": "recurrence_not_contained",
                "guardrail_effective": False,
            },
            "repair_kind": "tighten_gate",
            "target": "candidate policy bridge",
            "rationale": "make candidate capital decisions use policy_engine as the single policy source",
            "path": "capital_filter.py",
            "change_summary": "delegate candidate capital policy decision to policy_engine.evaluate_trade",
            "expected_test": "research_lab.test_product_policy_bridge",
        },
    )
    assert planned["controller_state"] == "write"
    assert planned["execution_plan"]["path"] == "capital_filter.py"

    for price in (8_000, 10_000, 12_000):
        candidate = _candidate(price)
        candidate_decision = evaluate_capital_fit(10_000, candidate)
        policy_decision = evaluate_trade(10_000, _legacy(candidate))

        assert candidate_decision["allowed"] == policy_decision["allowed"]
        assert candidate_decision["policy_version"] == POLICY_VERSION
        assert (
            candidate_decision["rule_summary"]["full_capital_purchase_required"]
            == policy_decision["rule_summary"]["full_capital_purchase_required"]
        )


if __name__ == "__main__":
    main()
