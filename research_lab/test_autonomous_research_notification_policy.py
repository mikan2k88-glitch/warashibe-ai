"""Offline tests for autonomous research notification policy."""

from research_lab.autonomous_research_notification_policy import (
    NOTIFICATION_POLICY_VERSION,
    notification_decision,
    validate_notification_policy,
)


def main():
    assert NOTIFICATION_POLICY_VERSION == "0.1"
    assert validate_notification_policy() is True

    for status in ("human_gate", "audit_failed", "failed"):
        decision = notification_decision(summary={"status": status})
        assert decision["notify"] is True
        assert decision["reason"] == status
        assert decision["notification_sent"] is False

    stopped = notification_decision(summary={"status": "stopped"})
    assert stopped["notify"] is False

    changed = notification_decision(
        summary={"status": "completed"},
        meaningful_change=True,
    )
    assert changed["notify"] is True
    assert changed["reason"] == "meaningful_change"

    try:
        notification_decision(summary={"status": "completed"}, meaningful_change=1)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")

    assert notification_decision(
        summary={"status": None}
    )["reason"] == "unknown_status_requires_attention"

    print("Autonomous research notification policy tests passed")


if __name__ == "__main__":
    main()
