"""Offline repair-candidate proposal for recurring guardrail failures.

This module only proposes one reviewable repair candidate when an unsafe pattern
has recurred and was not contained. It never edits code, prompts, policies,
permissions, workflows, or external systems and never authorizes execution.
"""

_ALLOWED_REPAIR_KINDS = {
    "add_validation",
    "add_test",
    "tighten_gate",
    "improve_logging",
    "clarify_instruction",
}


def propose_repair_candidate(recurrence_result, *, repair_kind, target, rationale):
    base = {
        "status": "hold_repair_candidate",
        "reviewable": False,
        "repair_candidate": None,
        "external_action_authorized": False,
        "auto_repair_authorized": False,
        "max_repairs_this_cycle": 1,
        "reasons": (),
    }

    if not isinstance(recurrence_result, dict):
        return dict(base, reasons=("invalid_recurrence_result",))

    if recurrence_result.get("status") != "recurrence_not_contained":
        return dict(base, reasons=("recurrence_not_actionable",))

    if recurrence_result.get("guardrail_effective") is not False:
        return dict(base, reasons=("guardrail_failure_not_confirmed",))

    if repair_kind not in _ALLOWED_REPAIR_KINDS:
        return dict(base, reasons=("repair_kind_not_allowed",))

    for value in (target, rationale):
        if not isinstance(value, str) or not value.strip():
            return dict(base, reasons=("invalid_repair_description",))

    lowered = f"{target} {rationale}".lower()
    forbidden_terms = (
        "main",
        "production",
        "secret",
        "credential",
        "payment",
        "purchase",
        "trade",
        "live db",
        "permission expansion",
    )
    if any(term in lowered for term in forbidden_terms):
        return dict(base, reasons=("repair_scope_not_allowed",))

    candidate = {
        "repair_kind": repair_kind,
        "target": target.strip(),
        "rationale": rationale.strip(),
        "scope": "research-lab",
        "requires_review": True,
        "single_repair_only": True,
    }

    return dict(
        base,
        status="repair_candidate_reviewable",
        reviewable=True,
        repair_candidate=candidate,
        reasons=(),
    )
