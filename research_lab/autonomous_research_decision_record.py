"""Secret-safe decision records for autonomous research cycles.

Records explain why a cycle proceeded or stopped without performing or
authorizing any external action.
"""

from datetime import datetime, timezone

from research_lab.autonomous_research_orchestrator_design import classify_action

DECISION_RECORD_VERSION = "0.1"
ALLOWED_DECISIONS = ("proceed", "repair", "human_gate", "stop")


def build_decision_record(*, action, decision, reason, stage, next_theme=None):
    if decision not in ALLOWED_DECISIONS:
        raise ValueError("unsupported decision")
    if not all(isinstance(value, str) and value.strip() for value in (action, reason, stage)):
        raise ValueError("action, reason, and stage must be non-empty strings")
    if next_theme is not None and (not isinstance(next_theme, str) or not next_theme.strip()):
        raise ValueError("next_theme must be a non-empty string or None")

    classification = classify_action(action)
    if classification == "human_gate" and decision != "human_gate":
        raise ValueError("human-gated action cannot proceed autonomously")
    if classification == "stop_unknown" and decision != "stop":
        raise ValueError("unknown action must stop")

    return {
        "version": DECISION_RECORD_VERSION,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "next_theme": next_theme,
        "action": action,
        "classification": classification,
        "decision": decision,
        "reason": reason,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_decision_record():
    record = build_decision_record(
        action="edit_research_lab_code",
        decision="proceed",
        reason="bounded research change",
        stage="decision_record",
        next_theme="example_next_theme",
    )
    assert record["classification"] == "autonomous"
    assert record["external_action_performed"] is False
    assert record["credentials_included"] is False
    return True
