"""Offline tests for autonomous research execution receipts."""

from research_lab.autonomous_research_execution_receipt import (
    EXECUTION_RECEIPT_VERSION,
    build_execution_receipt,
    validate_execution_receipt,
)


def expect_value_error(**kwargs):
    try:
        build_execution_receipt(**kwargs)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def main():
    assert EXECUTION_RECEIPT_VERSION == "0.1"
    assert validate_execution_receipt() is True

    blocked_plan = {
        "decision": "human_gate",
        "steps": ("stop_for_human_approval",),
        "reason": "action_requires_human_approval",
        "external_action_performed": False,
    }
    blocked = build_execution_receipt(
        execution_plan=blocked_plan,
        result="blocked",
        completed_steps=("stop_for_human_approval",),
    )
    assert blocked["decision"] == "human_gate"
    assert blocked["credentials_included"] is False

    expect_value_error(
        execution_plan=blocked_plan,
        result="completed",
        completed_steps=("execute_supabase_ddl",),
    )
    expect_value_error(
        execution_plan={**blocked_plan, "external_action_performed": True},
        result="completed",
    )
    expect_value_error(
        execution_plan=blocked_plan,
        result="unsupported",
    )

    print("Autonomous research execution receipt tests passed")


if __name__ == "__main__":
    main()
