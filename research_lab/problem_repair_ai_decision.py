"""AI-only decision gate for bounded research-lab code repairs.

There is intentionally no human approval step for ordinary code-repair decisions.
The AI may authorize one bounded repair when all machine-checkable constraints pass.
This module never authorizes MAIN/production, secrets, live DB, payments, commerce,
permission expansion, or external runtime actions.
"""

_ALLOWED_REPAIR_KINDS = {
    "add_validation",
    "add_test",
    "tighten_gate",
    "improve_logging",
    "clarify_instruction",
}


def decide_ai_code_repair(repair_result):
    base = {
        "status": "hold_ai_repair",
        "decision_authority": "ai",
        "human_gate_required": False,
        "code_repair_authorized": False,
        "external_runtime_action_authorized": False,
        "max_repairs_this_cycle": 1,
        "reasons": (),
    }

    if not isinstance(repair_result, dict):
        return dict(base, reasons=("invalid_repair_result",))

    if repair_result.get("status") != "repair_candidate_reviewable":
        return dict(base, reasons=("repair_candidate_not_reviewable",))

    candidate = repair_result.get("repair_candidate")
    if not isinstance(candidate, dict):
        return dict(base, reasons=("missing_repair_candidate",))

    if candidate.get("scope") != "research-lab":
        return dict(base, reasons=("scope_not_allowed",))

    if candidate.get("repair_kind") not in _ALLOWED_REPAIR_KINDS:
        return dict(base, reasons=("repair_kind_not_allowed",))

    if candidate.get("single_repair_only") is not True:
        return dict(base, reasons=("single_repair_limit_missing",))

    target = candidate.get("target")
    rationale = candidate.get("rationale")
    if not isinstance(target, str) or not target.strip():
        return dict(base, reasons=("invalid_target",))
    if not isinstance(rationale, str) or not rationale.strip():
        return dict(base, reasons=("invalid_rationale",))

    text = f"{target} {rationale}".lower()
    forbidden = (
        "main",
        "production",
        "secret",
        "credential",
        "payment",
        "purchase",
        "trade",
        "live db",
        "permission expansion",
        "external ai",
    )
    if any(term in text for term in forbidden):
        return dict(base, reasons=("repair_scope_not_allowed",))

    return dict(
        base,
        status="ai_repair_authorized",
        code_repair_authorized=True,
        reasons=(),
    )
