"""PG-036 Live Pilot Review.

Reviews one completed Warashibe cycle against its Sale Plan predictions.
Synthetic evidence remains explicitly non-live and never authorizes controlled
automation. The output is suitable as Learning Loop feedback.
"""

from datetime import datetime, timezone

REVIEW_VERSION="0.1"


def _text(value,name,max_length=300):
    if not isinstance(value,str) or not value.strip():
        raise ValueError(f"{name} is required")
    value=value.strip()
    if len(value)>max_length:
        raise ValueError(f"{name} is too long")
    return value


def _utc(value,name):
    value=_text(value,name,80)
    text=value[:-1]+"+00:00" if value.endswith("Z") else value
    dt=datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"{name} must include timezone")
    return dt.astimezone(timezone.utc)


def _number(value,name):
    if isinstance(value,bool) or not isinstance(value,(int,float)):
        raise ValueError(f"{name} must be numeric")
    return float(value)


def review_pilot_cycle(*,sale_plan,cycle_proof,review_key,reviewed_at):
    if not isinstance(sale_plan,dict) or sale_plan.get("status")!="sale_plan_ready":
        raise ValueError("sale_plan_ready required")
    if not isinstance(cycle_proof,dict) or cycle_proof.get("status")!="one_cycle_warashibe_proved":
        raise ValueError("one_cycle_warashibe_proved required")
    if sale_plan.get("item_key")!=cycle_proof.get("item_key"):
        raise ValueError("item_key mismatch")
    if sale_plan.get("quantity")!=1 or cycle_proof.get("quantity")!=1:
        raise ValueError("exactly one item required")
    if cycle_proof.get("chain_consistent") is not True:
        raise ValueError("consistent cycle proof required")
    if cycle_proof.get("warashibe_loop_v2_contract_complete") is not True:
        raise ValueError("Warashibe Loop v2 completion required")
    if cycle_proof.get("controlled_automation_authorized") is not False:
        raise ValueError("input proof must not pre-authorize automation")

    expected_net=_number(sale_plan.get("expected_net_proceeds_jpy"),"expected_net_proceeds_jpy")
    expected_profit=_number(sale_plan.get("expected_profit_jpy"),"expected_profit_jpy")
    expected_days=_number(sale_plan.get("estimated_days_to_sell"),"estimated_days_to_sell")
    expected_velocity=_number(
        sale_plan.get("expected_capital_velocity_jpy_per_day"),
        "expected_capital_velocity_jpy_per_day",
    )

    actual_net=_number(cycle_proof.get("actual_net_proceeds_jpy"),"actual_net_proceeds_jpy")
    actual_profit=_number(cycle_proof.get("capital_growth_jpy"),"capital_growth_jpy")
    actual_days=_number(cycle_proof.get("cycle_elapsed_days"),"cycle_elapsed_days")
    actual_velocity=_number(
        cycle_proof.get("capital_velocity_jpy_per_day"),
        "capital_velocity_jpy_per_day",
    )

    errors={
        "net_proceeds_jpy":int(round(actual_net-expected_net)),
        "profit_jpy":int(round(actual_profit-expected_profit)),
        "days_to_sell":round(actual_days-expected_days,4),
        "capital_velocity_jpy_per_day":round(actual_velocity-expected_velocity,2),
    }
    live_verified=cycle_proof.get("live_external_actions_verified") is True
    mode="live_verified_review" if live_verified else "synthetic_cycle_review"

    return {
        "version":REVIEW_VERSION,
        "status":"live_pilot_review_complete",
        "review_key":_text(review_key,"review_key",200),
        "proof_key":cycle_proof.get("proof_key"),
        "plan_key":sale_plan.get("plan_key"),
        "item_key":cycle_proof.get("item_key"),
        "quantity":1,
        "review_mode":mode,
        "proof_mode":cycle_proof.get("proof_mode"),
        "prediction_error":errors,
        "expected":{
            "net_proceeds_jpy":int(round(expected_net)),
            "profit_jpy":int(round(expected_profit)),
            "days_to_sell":expected_days,
            "capital_velocity_jpy_per_day":expected_velocity,
        },
        "actual":{
            "net_proceeds_jpy":int(round(actual_net)),
            "profit_jpy":int(round(actual_profit)),
            "days_to_sell":actual_days,
            "capital_velocity_jpy_per_day":actual_velocity,
            "next_capital_jpy":cycle_proof.get("next_capital_jpy"),
        },
        "reviewed_at":_utc(reviewed_at,"reviewed_at").isoformat(),
        "warashibe_loop_v2_contract_complete":True,
        "live_pilot_verified":live_verified,
        "learning_loop_feedback_ready":True,
        "eligible_for_controlled_automation":False,
        "controlled_automation_authorized":False,
        "human_decision_required":True,
    }
