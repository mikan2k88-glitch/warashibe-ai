"""Offline problem-to-guardrail candidate synthesis.

This module converts a structured problem record into a reviewable guardrail
candidate. It does not modify prompts, policies, permissions, workflows, or
external systems and never authorizes execution.
"""

_ALLOWED_CLASSES = {
    "ci_failure",
    "safety_block",
    "duplicate_action",
    "evidence_mismatch",
    "api_error",
}


def propose_guardrail_candidate(problem):
    base = {
        "status": "hold_guardrail_candidate",
        "reviewable": False,
        "candidate": None,
        "external_action_authorized": False,
        "auto_apply": False,
        "reasons": (),
    }

    if not isinstance(problem, dict):
        return dict(base, reasons=("invalid_problem_record",))

    required = (
        "problem_id",
        "problem_class",
        "trigger",
        "blocked_or_failed_action",
        "safe_expected_behavior",
        "evidence_ref",
    )
    if any(not isinstance(problem.get(k), str) or not problem.get(k).strip()
           for k in required):
        return dict(base, reasons=("missing_required_field",))

    if problem["problem_class"] not in _ALLOWED_CLASSES:
        return dict(base, reasons=("unknown_problem_class",))

    if problem.get("resolved") is True:
        return dict(base, reasons=("problem_already_resolved",))

    if problem.get("requires_permission_expansion") is True:
        return dict(base, reasons=("permission_expansion_not_allowed",))

    if problem.get("touches_live_commerce") is True:
        return dict(base, reasons=("live_commerce_out_of_scope",))

    candidate = {
        "candidate_id": f"guardrail:{problem['problem_id']}",
        "problem_class": problem["problem_class"],
        "when": problem["trigger"].strip(),
        "prevent": problem["blocked_or_failed_action"].strip(),
        "instead": problem["safe_expected_behavior"].strip(),
        "evidence_ref": problem["evidence_ref"].strip(),
        "scope": "research-lab",
    }

    return dict(
        base,
        status="guardrail_candidate_reviewable",
        reviewable=True,
        candidate=candidate,
        reasons=(),
    )
