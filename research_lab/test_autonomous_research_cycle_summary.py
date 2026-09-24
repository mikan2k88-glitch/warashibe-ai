"""Offline tests for autonomous research cycle summaries."""

from research_lab.autonomous_research_cycle_summary import (
    CYCLE_SUMMARY_VERSION,
    build_cycle_summary,
    validate_cycle_summary,
)


def summary(decision, result, audit_passed=True, issues=()):
    return build_cycle_summary(
        execution_plan={
            "decision": decision,
            "reason": "test_reason",
            "steps": ("step_a",),
        },
        receipt={"result": result, "completed_steps": ()},
        audit={"passed": audit_passed, "issues": issues},
    )


def main():
    assert CYCLE_SUMMARY_VERSION == "0.1"
    assert validate_cycle_summary() is True

    gated = summary("human_gate", "blocked")
    assert gated["status"] == "human_gate"
    assert gated["human_attention_required"] is True

    stopped = summary("stop", "blocked")
    assert stopped["status"] == "stopped"
    assert stopped["human_attention_required"] is False

    audit_failed = summary("proceed", "completed", False, ("decision_mismatch",))
    assert audit_failed["status"] == "audit_failed"
    assert audit_failed["audit_issue_count"] == 1
    assert audit_failed["human_attention_required"] is True

    failed = summary("repair", "failed")
    assert failed["status"] == "failed"
    assert failed["human_attention_required"] is True

    incomplete = summary("proceed", "planned")
    assert incomplete["status"] == "incomplete"

    print("Autonomous research cycle summary tests passed")


if __name__ == "__main__":
    main()
