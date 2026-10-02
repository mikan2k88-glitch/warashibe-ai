from candidate_engine import create_candidate
from research_lab.repair_execution_controller import control_repair_execution


REQUIRED_EVALUATION_FIELDS = (
    "purchase_price",
    "expected_sale_price",
    "liquidity_score",
    "estimated_days_to_sell",
    "estimated_fees",
    "authenticity_status",
    "return_risk",
    "physical",
)


def main():
    planned = control_repair_execution(
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
    assert planned["controller_state"] == "write"
    assert planned["execution_plan"]["path"] == "candidate_engine.py"

    incomplete = create_candidate(
        name="incomplete",
        purchase_price=3_000,
        expected_sale_price=4_500,
        source="test",
        confidence=0.8,
    )
    evaluation = incomplete["evaluation"]
    assert tuple(evaluation.keys()) == REQUIRED_EVALUATION_FIELDS
    assert evaluation["purchase_price"] == 3_000
    assert evaluation["expected_sale_price"] == 4_500
    assert evaluation["liquidity_score"] is None
    assert evaluation["estimated_days_to_sell"] is None
    assert evaluation["estimated_fees"] is None
    assert evaluation["authenticity_status"] == "unassessed"
    assert evaluation["return_risk"] == "unassessed"
    assert evaluation["physical"]["policy"]["allowed"] is False
    assert evaluation["physical"]["policy"]["physical_fit"] == "insufficient_data"

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
        package_size_class="compact",
        weight_grams=350,
        shipping_cost_jpy=450,
        fragility_score=0.1,
        storage_score=0.9,
        domestic_shipping=True,
    )
    evaluation = complete["evaluation"]
    assert evaluation["liquidity_score"] == 0.7
    assert evaluation["estimated_days_to_sell"] == 7
    assert evaluation["estimated_fees"] == 450
    assert evaluation["authenticity_status"] == "verified"
    assert evaluation["return_risk"] == "low"
    assert evaluation["physical"]["package_size_class"] == "compact"
    assert evaluation["physical"]["weight_grams"] == 350
    assert evaluation["physical"]["policy"]["allowed"] is True


if __name__ == "__main__":
    main()
