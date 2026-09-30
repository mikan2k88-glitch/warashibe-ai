"""Bounded execution-plan gate for AI-authorized research-lab code repairs.

This module does not edit files itself. It validates a single proposed patch plan
for an AI-authorized low-risk repair. Human approval is intentionally not part of
this ordinary research-lab repair path.
"""

_ALLOWED_PREFIXES = ("research_lab/",)
_ALLOWED_SUFFIXES = (".py",)


def build_repair_execution_plan(ai_decision, *, path, change_summary, expected_test):
    base = {
        "status": "hold_repair_execution",
        "decision_authority": "ai",
        "human_gate_required": False,
        "git_write_authorized": False,
        "external_runtime_action_authorized": False,
        "max_files_changed": 1,
        "max_repairs_this_cycle": 1,
        "plan": None,
        "reasons": (),
    }

    if not isinstance(ai_decision, dict):
        return dict(base, reasons=("invalid_ai_decision",))

    if ai_decision.get("status") != "ai_repair_authorized":
        return dict(base, reasons=("ai_repair_not_authorized",))

    if ai_decision.get("code_repair_authorized") is not True:
        return dict(base, reasons=("code_repair_not_authorized",))

    for value in (path, change_summary, expected_test):
        if not isinstance(value, str) or not value.strip():
            return dict(base, reasons=("invalid_execution_plan",))

    normalized = path.strip().replace("\\", "/")
    if normalized.startswith("/") or ".." in normalized.split("/"):
        return dict(base, reasons=("path_not_allowed",))

    if not normalized.startswith(_ALLOWED_PREFIXES):
        return dict(base, reasons=("path_not_allowed",))

    if not normalized.endswith(_ALLOWED_SUFFIXES):
        return dict(base, reasons=("file_type_not_allowed",))

    lowered = f"{normalized} {change_summary} {expected_test}".lower()
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
        "delete repository",
        "force push",
    )
    if any(term in lowered for term in forbidden):
        return dict(base, reasons=("execution_scope_not_allowed",))

    plan = {
        "path": normalized,
        "change_summary": change_summary.strip(),
        "expected_test": expected_test.strip(),
        "branch": "research-lab",
        "single_file_only": True,
        "requires_same_sha_ci_after_write": True,
        "stop_on_ci_failure_or_unknown": True,
    }

    return dict(
        base,
        status="repair_execution_plan_ready",
        git_write_authorized=True,
        plan=plan,
        reasons=(),
    )
