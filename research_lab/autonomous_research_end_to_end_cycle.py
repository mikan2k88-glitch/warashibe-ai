"""Pure end-to-end composition for one autonomous research cycle.

This connects the existing planning, receipt, audit, summary, notification,
and report contracts. It simulates cycle outcomes only and performs no external
actions.
"""

from research_lab.autonomous_research_execution_plan import build_execution_plan
from research_lab.autonomous_research_execution_receipt import build_execution_receipt
from research_lab.autonomous_research_cycle_audit import audit_cycle
from research_lab.autonomous_research_cycle_summary import build_cycle_summary
from research_lab.autonomous_research_notification_policy import notification_decision
from research_lab.autonomous_research_cycle_report import build_cycle_report

END_TO_END_CYCLE_VERSION = "0.1"


def run_end_to_end_cycle(
    *,
    result="planned",
    completed_steps=(),
    meaningful_change=False,
    **cycle_kwargs,
):
    plan = build_execution_plan(**cycle_kwargs)
    receipt = build_execution_receipt(
        execution_plan=plan,
        result=result,
        completed_steps=completed_steps,
    )
    audit = audit_cycle(execution_plan=plan, receipt=receipt)
    summary = build_cycle_summary(
        execution_plan=plan,
        receipt=receipt,
        audit=audit,
    )
    notification = notification_decision(
        summary=summary,
        meaningful_change=meaningful_change,
    )
    report = build_cycle_report(summary=summary, notification=notification)
    return {
        "version": END_TO_END_CYCLE_VERSION,
        "plan": plan,
        "receipt": receipt,
        "audit": audit,
        "summary": summary,
        "notification": notification,
        "report": report,
        "external_action_performed": False,
    }


def validate_end_to_end_cycle():
    cycle = run_end_to_end_cycle(
        state="inspect",
        action="edit_research_lab_code",
        stage="end_to_end_cycle",
        result="completed",
        completed_steps=(
            "prepare_research_change",
            "run_offline_tests",
            "request_ci_verification",
        ),
        meaningful_change=True,
    )
    assert cycle["plan"]["decision"] == "proceed"
    assert cycle["audit"]["passed"] is True
    assert cycle["summary"]["status"] == "completed"
    assert cycle["notification"]["notify"] is True
    assert cycle["report"]["notify"] is True
    assert cycle["external_action_performed"] is False
    return True
