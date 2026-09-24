"""Notification policy for autonomous research cycle summaries.

The policy decides whether a cycle is meaningful enough to surface to a human.
It creates metadata only and sends no notification itself.
"""

NOTIFICATION_POLICY_VERSION = "0.1"

NOTIFY_STATUSES = ("human_gate", "audit_failed", "failed")
SILENT_STATUSES = ("incomplete", "stopped")


def notification_decision(*, summary, meaningful_change=False):
    if not isinstance(summary, dict):
        raise ValueError("summary must be a dict")
    if not isinstance(meaningful_change, bool):
        raise ValueError("meaningful_change must be bool")

    status = summary.get("status")
    if status in NOTIFY_STATUSES:
        notify = True
        reason = status
    elif status == "completed" and meaningful_change:
        notify = True
        reason = "meaningful_change"
    elif status in SILENT_STATUSES or status == "completed":
        notify = False
        reason = "no_notification_needed"
    else:
        notify = True
        reason = "unknown_status_requires_attention"

    return {
        "version": NOTIFICATION_POLICY_VERSION,
        "notify": notify,
        "reason": reason,
        "status": status,
        "notification_sent": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_notification_policy():
    assert notification_decision(
        summary={"status": "human_gate"}
    )["notify"] is True
    assert notification_decision(
        summary={"status": "completed"}, meaningful_change=True
    )["notify"] is True
    assert notification_decision(
        summary={"status": "completed"}, meaningful_change=False
    )["notify"] is False
    assert notification_decision(
        summary={"status": "incomplete"}
    )["notify"] is False
    assert notification_decision(
        summary={"status": "unexpected"}
    )["notify"] is True
    return True
