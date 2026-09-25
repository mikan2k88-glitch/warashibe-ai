"""Runtime boundary contract for future Codex MCP execution.

All repository code, including main, may be modified when explicitly authorized
by the Warashibe Orchestrator. Sensitive non-code actions remain separately
gated. This module performs no MCP connection and invokes no Codex process.
"""

from research_lab.codex_orchestrator_security_policy import (
    CODE_BRANCHES,
    validate_orchestrator_code_task,
)

CODEX_MCP_RUNTIME_BOUNDARY_VERSION = "0.2"

REQUIRED_RUNTIME_STATE = (
    "latest_ci_green",
    "repository_workspace_ready",
    "codex_mcp_server_ready",
    "single_task_payload_ready",
    "orchestrator_security_ready",
    "human_gate_approved",
)

REQUIRED_TASK_FIELDS = (
    "milestone_id",
    "cycle_id",
    "task_id",
    "goal",
    "branch",
    "requested_capabilities",
    "max_repairs",
    "orchestrator_authorized",
)

REQUIRED_RESULT_FIELDS = (
    "task_id",
    "status",
    "branch",
    "changed_files",
    "test_command",
    "test_passed",
    "diff_summary",
    "human_gate_encountered",
    "policy_violation_detected",
)

ALLOWED_STATUSES = (
    "completed",
    "blocked",
    "failed",
    "human_gate_required",
)


def build_runtime_boundary():
    return {
        "version": CODEX_MCP_RUNTIME_BOUNDARY_VERSION,
        "mode": "design_only",
        "transport": "mcp_stdio_or_local_managed_transport",
        "workspace_scope": "entire_repository_codebase",
        "allowed_code_branches": CODE_BRANCHES,
        "allowed_path_scope": "all_repository_code",
        "security_owner": "warashibe_orchestrator",
        "main_code_changes_allowed": True,
        "single_task_per_invocation": True,
        "max_repairs_per_cycle": 1,
        "require_clean_task_envelope": True,
        "require_result_envelope": True,
        "require_offline_tests": True,
        "require_diff_summary": True,
        "require_changed_file_list": True,
        "require_ci_green_before_next_task": True,
        "stop_on_orchestrator_denial": True,
        "stop_on_policy_violation": True,
        "stop_on_unknown_status": True,
        "sensitive_non_code_actions_require_human_gate": True,
        "codex_mcp_connect_authorized": False,
        "codex_process_start_authorized": False,
        "workspace_write_authorized": False,
        "external_action_authorized": False,
    }


def validate_runtime_state(state):
    if not isinstance(state, dict):
        return {
            "ready": False,
            "errors": ("state_not_mapping",),
            "connect_authorized": False,
        }

    errors = []
    for field in REQUIRED_RUNTIME_STATE:
        if state.get(field) is not True:
            errors.append(f"missing_{field}")

    return {
        "ready": not errors,
        "errors": tuple(errors),
        "connect_authorized": False,
        "requires_one_shot_gate_consumption": True,
    }


def validate_task_envelope(task):
    if not isinstance(task, dict):
        return {
            "valid": False,
            "errors": ("task_not_mapping",),
        }

    errors = []
    for field in REQUIRED_TASK_FIELDS:
        if field not in task:
            errors.append(f"missing_{field}")

    if task.get("max_repairs") != 1:
        errors.append("invalid_max_repairs")

    goal = task.get("goal")
    if not isinstance(goal, str) or not goal.strip():
        errors.append("invalid_goal")

    security = validate_orchestrator_code_task(task)
    errors.extend(security.get("errors", ()))

    return {
        "valid": not errors,
        "errors": tuple(dict.fromkeys(errors)),
        "code_write_scope": security.get("code_write_scope"),
    }


def validate_result_envelope(result):
    if not isinstance(result, dict):
        return {
            "valid": False,
            "errors": ("result_not_mapping",),
            "safe_to_commit": False,
        }

    errors = []
    for field in REQUIRED_RESULT_FIELDS:
        if field not in result:
            errors.append(f"missing_{field}")

    status = result.get("status")
    if status not in ALLOWED_STATUSES:
        errors.append("unsupported_status")

    if result.get("branch") not in CODE_BRANCHES:
        errors.append("branch_not_allowed")

    changed_files = result.get("changed_files")
    if not isinstance(changed_files, (list, tuple)):
        errors.append("invalid_changed_files")

    if not isinstance(result.get("test_passed"), bool):
        errors.append("invalid_test_passed")

    if not isinstance(result.get("human_gate_encountered"), bool):
        errors.append("invalid_human_gate_encountered")

    if not isinstance(result.get("policy_violation_detected"), bool):
        errors.append("invalid_policy_violation_detected")

    safe_to_commit = (
        not errors
        and status == "completed"
        and result.get("test_passed") is True
        and result.get("human_gate_encountered") is False
        and result.get("policy_violation_detected") is False
    )

    return {
        "valid": not errors,
        "errors": tuple(errors),
        "safe_to_commit": safe_to_commit,
        "commit_authorized": False,
    }


def validate_codex_mcp_runtime_boundary():
    boundary = build_runtime_boundary()
    assert boundary["mode"] == "design_only"
    assert boundary["workspace_scope"] == "entire_repository_codebase"
    assert boundary["allowed_code_branches"] == ("research-lab", "main")
    assert boundary["allowed_path_scope"] == "all_repository_code"
    assert boundary["security_owner"] == "warashibe_orchestrator"
    assert boundary["main_code_changes_allowed"] is True
    assert boundary["single_task_per_invocation"] is True
    assert boundary["max_repairs_per_cycle"] == 1
    assert boundary["require_ci_green_before_next_task"] is True
    assert boundary["stop_on_orchestrator_denial"] is True
    assert boundary["stop_on_policy_violation"] is True
    assert boundary["sensitive_non_code_actions_require_human_gate"] is True
    assert boundary["codex_mcp_connect_authorized"] is False
    assert boundary["codex_process_start_authorized"] is False
    assert boundary["workspace_write_authorized"] is False
    assert boundary["external_action_authorized"] is False
    return True
