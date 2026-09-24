"""Offline tests for autonomous research decision records."""

from research_lab.autonomous_research_decision_record import (
    DECISION_RECORD_VERSION,
    build_decision_record,
    validate_decision_record,
)


def expect_value_error(**kwargs):
    try:
        build_decision_record(**kwargs)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def main():
    assert DECISION_RECORD_VERSION == "0.1"
    assert validate_decision_record() is True

    gated = build_decision_record(
        action="execute_supabase_ddl",
        decision="human_gate",
        reason="explicit approval required",
        stage="schema_migration",
    )
    assert gated["classification"] == "human_gate"
    assert gated["decision"] == "human_gate"

    expect_value_error(
        action="execute_supabase_ddl",
        decision="proceed",
        reason="unsafe",
        stage="schema_migration",
    )
    expect_value_error(
        action="undefined_action",
        decision="proceed",
        reason="unknown",
        stage="unknown",
    )
    expect_value_error(
        action="edit_research_lab_code",
        decision="unsupported",
        reason="bad decision",
        stage="test",
    )

    print("Autonomous research decision record tests passed")


if __name__ == "__main__":
    main()
