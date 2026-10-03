"""PG-036 Live Pilot Review contract tests."""

from research_lab.live_pilot_review import review_pilot_cycle


def main():
    plan={
        "status":"sale_plan_ready","plan_key":"plan-036","item_key":"item-036","quantity":1,
        "expected_net_proceeds_jpy":3390,"expected_profit_jpy":440,
        "estimated_days_to_sell":3,"expected_capital_velocity_jpy_per_day":146.67,
    }
    proof={
        "status":"one_cycle_warashibe_proved","proof_key":"proof-036","item_key":"item-036",
        "quantity":1,"proof_mode":"synthetic_auditable_cycle","chain_consistent":True,
        "starting_capital_jpy":3000,"actual_net_proceeds_jpy":3390,
        "next_capital_jpy":3440,"capital_growth_jpy":440,
        "cycle_elapsed_days":3.0208,"capital_velocity_jpy_per_day":145.66,
        "warashibe_loop_v2_contract_complete":True,
        "live_external_actions_verified":False,"controlled_automation_authorized":False,
    }
    review=review_pilot_cycle(
        sale_plan=plan,
        cycle_proof=proof,
        review_key="pilot-review-036",
        reviewed_at="2026-10-06T07:00:00+00:00",
    )
    assert review["status"]=="live_pilot_review_complete"
    assert review["prediction_error"]["net_proceeds_jpy"]==0
    assert review["prediction_error"]["profit_jpy"]==0
    assert review["prediction_error"]["days_to_sell"]==0.0208
    assert review["prediction_error"]["capital_velocity_jpy_per_day"]==-1.01
    assert review["warashibe_loop_v2_contract_complete"] is True
    assert review["live_pilot_verified"] is False
    assert review["eligible_for_controlled_automation"] is False
    assert review["human_decision_required"] is True
    assert review["learning_loop_feedback_ready"] is True

    print("PG-036 Live Pilot Review tests passed")


if __name__=="__main__":
    main()
