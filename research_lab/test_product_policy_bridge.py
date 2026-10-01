from capital_filter import _candidate_to_policy_item, evaluate_capital_fit
from candidate_engine import create_candidate
from candidate_strategy_adapter import candidate_to_strategy_item
from danger_filter import evaluate_candidate
from market_candidate_adapter import market_item_to_candidate
from ranking_engine import calculate_expected_value
import simulation_engine
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
            "change_summary": "delegate candidate capital decision to the shared policy engine",
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

    pg004_plan = control_repair_execution(
        state="plan",
        planning={
            "recurrence_result": {
                "status": "recurrence_not_contained",
                "guardrail_effective": False,
            },
            "repair_kind": "tighten_gate",
            "target": "candidate evaluation contract",
            "rationale": "normalize v1 product evaluation fields on every candidate",
            "path": "candidate_engine.py",
            "change_summary": "add a normalized evaluation contract with explicit unassessed values",
            "expected_test": "research_lab.test_product_candidate_contract",
        },
    )
    assert pg004_plan["controller_state"] == "write"
    assert pg004_plan["execution_plan"]["path"] == "candidate_engine.py"

    incomplete = create_candidate(
        name="incomplete",
        purchase_price=3_000,
        expected_sale_price=4_500,
        source="test",
        confidence=0.8,
    )
    evaluation = incomplete["evaluation"]
    assert evaluation["purchase_price"] == 3_000
    assert evaluation["expected_sale_price"] == 4_500
    assert evaluation["liquidity_score"] is None
    assert evaluation["estimated_days_to_sell"] is None
    assert evaluation["estimated_fees"] is None
    assert evaluation["authenticity_status"] == "unassessed"
    assert evaluation["return_risk"] == "unassessed"

    complete = create_candidate(
        name="complete",
        purchase_price=3_000,
        expected_sale_price=4_500,
        source="test",
        confidence=0.8,
        liquidity_score=0.7,
        estimated_days_to_sell=7,
        estimated_fees=450,
        authenticity_status="verified",
        return_risk="low",
    )
    evaluation = complete["evaluation"]
    assert evaluation["liquidity_score"] == 0.7
    assert evaluation["estimated_days_to_sell"] == 7
    assert evaluation["estimated_fees"] == 450
    assert evaluation["authenticity_status"] == "verified"
    assert evaluation["return_risk"] == "low"

    pg005_plan = control_repair_execution(
        state="plan",
        planning={
            "recurrence_result": {
                "status": "recurrence_not_contained",
                "guardrail_effective": False,
            },
            "repair_kind": "tighten_gate",
            "target": "candidate probability semantics",
            "rationale": "separate information confidence from success probability",
            "path": "candidate_engine.py",
            "change_summary": "add an explicit success probability field without changing confidence meaning",
            "expected_test": "research_lab.test_product_policy_bridge",
        },
    )
    assert pg005_plan["controller_state"] == "write"
    assert pg005_plan["execution_plan"]["path"] == "candidate_engine.py"

    separated = create_candidate(
        name="semantic split",
        purchase_price=3_000,
        expected_sale_price=4_500,
        source="test",
        confidence=0.9,
        success_probability=0.4,
    )
    assert separated["confidence"] == 0.9
    assert separated["success_probability"] == 0.4
    assert calculate_expected_value(separated) == 1_800

    risk = evaluate_candidate(separated)
    assert risk["information_confidence"] == 0.9
    assert risk["success_probability"] == 0.4
    assert risk["risk_level"] == "challenge"

    policy_item = _candidate_to_policy_item(separated)
    assert policy_item["success_rate"] == 0.4

    strategy_item = candidate_to_strategy_item(separated)
    assert strategy_item["success_rate"] == 0.4

    virtual = market_item_to_candidate({
        "name": "わら",
        "price": 3_000,
        "next_value": 4_500,
        "success_rate": 0.8,
    })
    assert virtual["confidence"] == 1.0
    assert virtual["success_probability"] == 0.8

    original_select_candidate_item = simulation_engine.select_candidate_item
    original_random = simulation_engine.random.random
    try:
        simulation_engine.select_candidate_item = lambda capital, strategy: {
            "name": "probability semantics",
            "purchase_price": 3_000,
            "expected_sale_price": 4_500,
            "confidence": 0.99,
            "success_probability": 0.4,
            "source": "test",
            "score": 1,
        }
        simulation_engine.random.random = lambda: 0.5
        simulation_result = simulation_engine.run_candidate_cycle("safe")
    finally:
        simulation_engine.select_candidate_item = original_select_candidate_item
        simulation_engine.random.random = original_random

    assert simulation_result["status"] == "failed"
    assert simulation_result["history"][0]["success_rate"] == 0.4
    assert simulation_result["history"][0]["random_value"] == 0.5

    pg005_repair = control_repair_execution(
        state="ci",
        write_evidence={
            "before_sha": "ea6374bd2db55b6a1937277b411d3516a7a19ff0",
            "after_sha": "6502be77815f4cd022cbcf60f19d5b1ba4f82469",
            "path": "simulation_engine.py",
            "expected_test": "research_lab.test_product_policy_bridge",
        },
        ci_evidence={
            "cycle_id": "product-gap-pg005-1065",
            "repair_id": "pg005-confidence-probability-separation",
            "observed_sha": "6502be77815f4cd022cbcf60f19d5b1ba4f82469",
            "ci_status": "completed",
            "ci_conclusion": "success",
        },
    )
    assert pg005_repair["status"] == "repair_pipeline_complete"
    assert pg005_repair["milestone_reached"] is True
    assert pg005_repair["next_action"] == "advance_problem_queue"
    assert pg005_repair["result"]["audit"]["status"] == "repair_audit_record_ready"
    assert pg005_repair["result"]["ledger"]["status"] == "repair_ledger_ready"

    pg004_repair = control_repair_execution(
        state="ci",
        write_evidence={
            "before_sha": "ad84f241be7e317e1512b497a3a079e9ed47d90f",
            "after_sha": "ebc4431a1f01a9d3d678a0a99ee71d827860f035",
            "path": "candidate_engine.py",
            "expected_test": "research_lab.test_product_policy_bridge",
        },
        ci_evidence={
            "cycle_id": "product-gap-pg004-1055",
            "repair_id": "pg004-candidate-evaluation-contract",
            "observed_sha": "ebc4431a1f01a9d3d678a0a99ee71d827860f035",
            "ci_status": "completed",
            "ci_conclusion": "success",
        },
    )
    assert pg004_repair["status"] == "repair_pipeline_complete"
    assert pg004_repair["milestone_reached"] is True
    assert pg004_repair["next_action"] == "advance_problem_queue"
    assert pg004_repair["result"]["audit"]["status"] == "repair_audit_record_ready"
    assert pg004_repair["result"]["ledger"]["status"] == "repair_ledger_ready"

    repair = control_repair_execution(
        state="ci",
        write_evidence={
            "before_sha": "ec5a15ac28da80029f5cc000b30d5f025ec676e4",
            "after_sha": "6791e7a8300af042485077497767aa7f2c1797e4",
            "path": "capital_filter.py",
            "expected_test": "research_lab.test_product_policy_bridge",
        },
        ci_evidence={
            "cycle_id": "product-gap-pg003-1050",
            "repair_id": "pg003-shared-policy-bridge",
            "observed_sha": "6791e7a8300af042485077497767aa7f2c1797e4",
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
