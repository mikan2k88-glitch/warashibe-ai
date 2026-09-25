"""Canonical task envelope sent from Warashibe Orchestrator to Codex MCP.

The envelope authorizes one bounded code task at a time. Repository-wide code
changes, including main, are allowed only when explicitly authorized by the
Orchestrator. Sensitive non-code actions remain separately gated.
"""

from research_lab.codex_orchestrator_security_policy import (
    CODE_BRANCHES,
    validate_orchestrator_code_task,
)

CODEX_MCP_TASK_ENVELOPE_VERSION = "0.1"

REQUIRED_FIELDS = (
    "envelope_version",
    "milestone_id",
    "cycle_id",
    "task_id",
    "goal",
    "branch",
    "requested_capabilities",
    "max_repairs",
    "orchestrator_authorized",
    "acceptance_checks",
    "stop_conditions",
)

DEFAULT_STOP_CONDITIONS = (
    "human_gate_required",
    "orchestrator_denied",
    "policy_violation",
    "unknown_capability",
    "test_failure_after_single_repair",
)


def build_codex_task_envelope(
    milestone_id,
    cycle_id,
    task_id,
    goal,
    branch,
    requested_capabilities,
    acceptance_checks,
    human_gate_approved=False,
):
    return {
        "envelope_version": CODEX_MCP_TASK_ENVELOPE_VERSION,
        "milestone_id": milestone_id,
        "cycle_id": cycle_id,
        "task_id": task_id,
        "goal": goal,
        "branch": branch,
        "requested_capabilities": tuple(requested_capabilities or ()),
        "max_repairs": 1,
        "orchestrator_authorized": True,
        "human_gate_approved": bool(human_gate_approved),
        "acceptance_checks": tuple(acceptance_checks or ()),
        "stop_conditions": DEFAULT_STOP_CONDITIONS,
        "require_offline_tests": True,
        "require_diff_summary": True,
        "require_changed_file_list": True,
        "require_result_envelope": True,
        "commit_authorized": False,
        "external_action_authorized": False,
    }


def validate_codex_task_envelope(envelope):
    if not isinstance(envelope, dict):
        return {
            "valid": False,
            "errors": ("envelope_not_mapping",),
            "execution_authorized": False,
        }

    errors = []

    for field in REQUIRED_FIELDS:
        if field not in envelope:
            errors.append(f"missing_{field}")

    if envelope.get("envelope_version") != CODEX_MCP_TASK_ENVELOPE_VERSION:
        errors.append("unsupported_envelope_version")

    if envelope.get("branch") not in CODE_BRANCHES:
        errors.append("branch_not_allowed")

    if envelope.get("max_repairs") != 1:
        errors.append("invalid_max_repairs")

    goal = envelope.get("goal")
    if not isinstance(goal, str) or not goal.strip():
        errors.append("invalid_goal")

    acceptance_checks = envelope.get("acceptance_checks")
    if not isinstance(acceptance_checks, (list, tuple)) or not acceptance_checks:
        errors.append("invalid_acceptance_checks")

    stop_conditions = envelope.get("stop_conditions")
    if tuple(stop_conditions or ()) != DEFAULT_STOP_CONDITIONS:
        errors.append("invalid_stop_conditions")

    security = validate_orchestrator_code_task(envelope)
    errors.extend(security.get("errors", ()))

    return {
        "valid": not errors,
        "errors": tuple(dict.fromkeys(errors)),
        "branch": envelope.get("branch"),
        "code_write_scope": security.get("code_write_scope"),
        "sensitive_capabilities": security.get("sensitive_capabilities", ()),
        "unknown_capabilities": security.get("unknown_capabilities", ()),
        "execution_authorized": False,
        "requires_codex_runtime_gate": True,
        "commit_authorized": False,
    }


def build_task_envelope_contract():
    return {
        "version": CODEX_MCP_TASK_ENVELOPE_VERSION,
        "mode": "design_only",
        "allowed_branches": CODE_BRANCHES,
        "repository_code_scope": "all_repository_code",
        "one_task_per_envelope": True,
        "max_repairs": 1,
        "orchestrator_authorization_required": True,
        "main_code_changes_allowed": True,
        "main_branch_write_requires_human_gate": True,
        "sensitive_non_code_actions_require_human_gate": True,
        "default_stop_conditions": DEFAULT_STOP_CONDITIONS,
        "commit_authorized": False,
        "codex_invocation_authorized": False,
        "external_action_authorized": False,
    }


def validate_codex_mcp_task_envelope_design():
    contract = build_task_envelope_contract()
    assert contract["mode"] == "design_only"
    assert contract["allowed_branches"] == ("research-lab", "main")
    assert contract["repository_code_scope"] == "all_repository_code"
    assert contract["one_task_per_envelope"] is True
    assert contract["max_repairs"] == 1
    assert contract["orchestrator_authorization_required"] is True
    assert contract["main_code_changes_allowed"] is True
    assert contract["main_branch_write_requires_human_gate"] is True
    assert contract["sensitive_non_code_actions_require_human_gate"] is True
    assert contract["commit_authorized"] is False
    assert contract["codex_invocation_authorized"] is False
    assert contract["external_action_authorized"] is False
    return True
