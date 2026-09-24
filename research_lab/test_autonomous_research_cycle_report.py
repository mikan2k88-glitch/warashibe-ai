"""Offline tests for autonomous research cycle reports."""

from research_lab.autonomous_research_cycle_report import (
    CYCLE_REPORT_VERSION,
    build_cycle_report,
    validate_cycle_report,
)


def make(status, notify, reason="test_reason"):
    summary = {
        "status": status,
        "decision": "human_gate" if status == "human_gate" else "proceed",
        "reason": reason,
        "result": "blocked" if status == "human_gate" else "completed",
        "audit_passed": status != "audit_failed",
        "audit_issue_count": 1 if status == "audit_failed" else 0,
        "human_attention_required": status in ("human_gate", "audit_failed", "failed"),
        "external_action_performed": False,
    }
    notification = {
        "status": status,
        "notify": notify,
        "reason": status if notify else "no_notification_needed",
        "external_action_performed": False,
    }
    return summary, notification


def main():
    assert CYCLE_REPORT_VERSION == "0.1"
    assert validate_cycle_report() is True

    summary, notification = make("human_gate", True)
    report = build_cycle_report(summary=summary, notification=notification)
    assert report["human_attention_required"] is True
    assert "human approval" in report["headline"]

    summary, notification = make("stopped", False)
    report = build_cycle_report(summary=summary, notification=notification)
    assert report["notify"] is False
    assert report["notification_sent"] is False

    summary, notification = make("completed", True)
    notification["status"] = "failed"
    try:
        build_cycle_report(summary=summary, notification=notification)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")

    summary, notification = make("completed", True)
    summary["external_action_performed"] = True
    try:
        build_cycle_report(summary=summary, notification=notification)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")

    print("Autonomous research cycle report tests passed")


if __name__ == "__main__":
    main()
