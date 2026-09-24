"""Human-facing report contract for one autonomous research cycle.

The report combines a secret-safe cycle summary with its notification decision.
It does not send messages or perform external actions.
"""

CYCLE_REPORT_VERSION = "0.1"


def build_cycle_report(*, summary, notification):
    if not isinstance(summary, dict) or not isinstance(notification, dict):
        raise ValueError("summary and notification must be dicts")
    if summary.get("status") != notification.get("status"):
        raise ValueError("summary and notification status must match")
    if summary.get("external_action_performed") is not False:
        raise ValueError("summary cannot claim external action")
    if notification.get("external_action_performed") is not False:
        raise ValueError("notification cannot claim external action")

    status = summary.get("status")
    report = {
        "version": CYCLE_REPORT_VERSION,
        "status": status,
        "decision": summary.get("decision"),
        "reason": summary.get("reason"),
        "result": summary.get("result"),
        "audit_passed": summary.get("audit_passed"),
        "audit_issue_count": summary.get("audit_issue_count", 0),
        "human_attention_required": summary.get("human_attention_required", False),
        "notify": notification.get("notify") is True,
        "notification_reason": notification.get("reason"),
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }
    report["headline"] = {
        "completed": "Autonomous research cycle completed",
        "human_gate": "Autonomous research cycle requires human approval",
        "audit_failed": "Autonomous research cycle audit failed",
        "failed": "Autonomous research cycle failed",
        "stopped": "Autonomous research cycle stopped safely",
        "incomplete": "Autonomous research cycle is incomplete",
    }.get(status, "Autonomous research cycle requires attention")
    return report


def validate_cycle_report():
    summary = {
        "status": "completed",
        "decision": "proceed",
        "reason": "bounded_autonomous_step",
        "result": "completed",
        "audit_passed": True,
        "audit_issue_count": 0,
        "human_attention_required": False,
        "external_action_performed": False,
    }
    notification = {
        "status": "completed",
        "notify": True,
        "reason": "meaningful_change",
        "external_action_performed": False,
    }
    report = build_cycle_report(summary=summary, notification=notification)
    assert report["headline"] == "Autonomous research cycle completed"
    assert report["notify"] is True
    assert report["notification_sent"] is False
    assert report["credentials_included"] is False
    return True
