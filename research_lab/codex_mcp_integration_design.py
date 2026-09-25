"""Design the Warashibe Orchestrator -> Codex MCP integration.

Security ownership is centralized in the Warashibe Orchestrator. Codex may
modify any repository code, including main, only when the Orchestrator has
authorized the task. This module does not invoke Codex.
"""

from research_lab.codex_orchestrator_security_policy import (
    CODE_BRANCHES,
    CODE_CAPABILITIES,
    SENSITIVE_NON_CODE_CAPABILITIES,
    validate_orchestrator_code_task,
)

CODEX_MCP_INTEGRATION_DESIGN_VERSION = "0.2"

ARCHITECTURE = (
    "warashibe_orchestrator",
    "codex_mcp_server",
    "repository_workspace",
    "orchestrator_security_policy",
    "offline_tests",
    "github_push",
    "ci_verification",
    "orchestrator_review",
)

REQUIRED_CONTROL_FIELDS = (
    "milestone_id",
    "cycle_id",
    "task_id",
    "branch",
    "max_repairs",
    "orchestrator_authorized",
)


def build_codex_mcp_request_contract():
    return {
        "version": CODEX_MCP_INTEGRATION_DESIGN_VERSION,
        "mode": "design_only",
        "transport": "mcp",
        "architecture": ARCHITECTURE,
        "allowed_code_branches": CODE_BRANCHES,
        "allowed_code_capabilities": CODE_CAPABILITIES,
        "sensitive_non_code_capabilities": SENSITIVE_NON_CODE_CAPABILITIES,
        "required_control_fields": REQUIRED_CONTROL_FIELDS,
        "repository_code_scope": "all_repository_code",
        "workspace_policy": "repository_wide_code_write",
        "security_owner": "warashibe_orchestrator",
        "main_code_changes_allowed": True,
        "one_theme_per_request": True,
        "max_repairs_per_cycle": 1,
        "require_offline_tests_before_commit": True,
        "require_ci_green_before_next_request": True,
        "stop_on_orchestrator_denial": True,
        "stop_on_unknown_capability": True,
        "sensitive_non_code_actions_require_human_gate": True,
        "codex_process_start_authorized": False,
        "mcp_connection_authorized": False,
        "external_action_authorized": False,
    }


def validate_codex_mcp_task(task):
    if not isinstance(task, dict):
        return {
            "valid": False,
            "errors": ("task_not_mapping",),
            "execution_authorized": False,
        }

    errors = []
    for field in REQUIRED_CONTROL_FIELDS:
        if field not in task:
            errors.append(f"missing_{field}")

    if task.get("max_repairs") != 1:
        errors.append("invalid_max_repairs")

    security = validate_orchestrator_code_task(task)
    errors.extend(security.get("errors", ()))

    return {
        "valid": not errors,
        "errors": tuple(dict.fromkeys(errors)),
        "sensitive_capabilities": security.get("sensitive_capabilities", ()),
        "unknown_capabilities": security.get("unknown_capabilities", ()),
        "execution_authorized": False,
        "requires_live_codex_gate": True,
    }


def build_codex_mcp_lifecycle():
    return {
        "version": CODEX_MCP_INTEGRATION_DESIGN_VERSION,
        "flow": (
            "orchestrator_selects_task",
            "orchestrator_authorizes_code_scope_and_branch",
            "build_codex_task",
            "validate_orchestrator_security_policy",
            "request_live_codex_gate",
            "send_single_task_over_mcp",
            "codex_edits_repository_code",
            "codex_runs_offline_tests",
            "codex_returns_diff_and_test_report",
            "orchestrator_reviews_result",
            "commit_authorized_branch",
            "inspect_ci",
            "repair_once_if_needed",
            "record_progress",
        ),
        "actual_codex_invocation_authorized": False,
        "actual_mcp_transport_authorized": False,
        "external_action_authorized": False,
    }


def validate_codex_mcp_integration_design():
    contract = build_codex_mcp_request_contract()
    assert contract["mode"] == "design_only"
    assert contract["allowed_code_branches"] == ("research-lab", "main")
    assert contract["repository_code_scope"] == "all_repository_code"
    assert contract["workspace_policy"] == "repository_wide_code_write"
    assert contract["security_owner"] == "warashibe_orchestrator"
    assert contract["main_code_changes_allowed"] is True
    assert contract["one_theme_per_request"] is True
    assert contract["max_repairs_per_cycle"] == 1
    assert contract["require_offline_tests_before_commit"] is True
    assert contract["require_ci_green_before_next_request"] is True
    assert contract["sensitive_non_code_actions_require_human_gate"] is True
    assert contract["codex_process_start_authorized"] is False
    assert contract["mcp_connection_authorized"] is False
    assert contract["external_action_authorized"] is False
    return True
