"""Offline recurrence check for reviewable problem guardrails.

The checker evaluates whether a previously observed problem pattern appears again.
It never changes policies, permissions, prompts, workflows, or external systems.
"""

def evaluate_guardrail_recurrence(candidate_result, event):
    base = {
        "status": "hold_recurrence_check",
        "recurrence_detected": False,
        "guardrail_effective": None,
        "external_action_authorized": False,
        "auto_repair_authorized": False,
        "reasons": (),
    }

    if not isinstance(candidate_result, dict) or not isinstance(event, dict):
        return dict(base, reasons=("invalid_input",))

    if candidate_result.get("status") != "guardrail_candidate_reviewable":
        return dict(base, reasons=("candidate_not_reviewable",))

    candidate = candidate_result.get("candidate")
    if not isinstance(candidate, dict):
        return dict(base, reasons=("missing_candidate",))

    required = ("problem_class", "when", "prevent", "instead", "evidence_ref", "scope")
    if any(not isinstance(candidate.get(k), str) or not candidate.get(k).strip()
           for k in required):
        return dict(base, reasons=("invalid_candidate",))

    if candidate.get("scope") != "research-lab":
        return dict(base, reasons=("scope_not_allowed",))

    event_required = ("problem_class", "trigger", "attempted_action", "outcome")
    if any(not isinstance(event.get(k), str) or not event.get(k).strip()
           for k in event_required):
        return dict(base, reasons=("invalid_event",))

    same_problem = (
        event["problem_class"] == candidate["problem_class"]
        and event["trigger"].strip() == candidate["when"]
        and event["attempted_action"].strip() == candidate["prevent"]
    )

    if not same_problem:
        return dict(
            base,
            status="no_matching_recurrence",
            guardrail_effective=None,
            reasons=(),
        )

    if event["outcome"] == "blocked_before_action":
        return dict(
            base,
            status="recurrence_contained",
            recurrence_detected=True,
            guardrail_effective=True,
            reasons=(),
        )

    if event["outcome"] in {"attempted", "completed"}:
        return dict(
            base,
            status="recurrence_not_contained",
            recurrence_detected=True,
            guardrail_effective=False,
            reasons=("unsafe_pattern_recurred",),
        )

    return dict(base, reasons=("unknown_event_outcome",))
