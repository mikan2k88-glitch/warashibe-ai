"""Runtime boundary contract for future Codex MCP execution.

This module defines connection, workspace, task payload, and result-envelope
requirements. It performs no MCP connection and invokes no Codex process.
"""

CODEX_MCP_RUNTIME_BOUNDARY_VERSION = "0.1"

REQUIRED_RUNTIME_STATE = (
    "latest_ci_green",
    "research_lab_branch_confirmed",
    "bounded_workspace_ready",
    "codex_mcp_server_ready",
    "single_task_payload_ready",
    "human_gate_approved",
)

REQUIRED_TASK_FIELDS = (
    "milestone_id",
    "cycle_id",
    "task_id",
    "goal",
    "allowed_branch",
    "allowed_paths",
    "requested_capabilities",
    "max_repairs",
)

REQUIRED_RESULT_FIELDS = (
    "task_id",
    "status",
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
        "workspace_scope": "bounded_repository_workspace",
        "allowed_branch": "research-lab",
        "allowed_path_prefixes": (
            "research_lab/",
            "real_world_engine.py",
            "real_world_api.py",
            "warashibe_core_mode.py",
        ),
        "single_task_per_invocation": True,
        "max_repairs_per_cycle": 1,
        "require_clean_task_envelope": True,
        "require_result_envelope": True,
        "require_offline_tests": True,
        "require_diff_summary": True,
        "require_changed_file_list": True,
        "require_ci_green_before_next_task": True,
        "stop_on_human_gate": True,
        "stop_on_policy_violation": True,
        "stop_on_unknown_status": True,
        "network_default": "deny",
        "secret_default": "deny",
        "commerce_default": "deny",
        "codex_mcp_connect_authorized": False,
        "codex_process_start_authorized": False,
        "workspace_write_authorized": False,
        "network_execution_authorized": False,
        "secret_access_authorized": False,
        "commerce_authorized": False,
        "production_change_authorized": False,
        "main_branch_change_authorized": False,
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

    if task.get("allowed_branch") != "research-lab":
        errors.append("branch_not_allowed")

    if task.get("max_repairs") != 1:
        errors.append("invalid_max_repairs")

    allowed_paths = task.get("allowed_paths")
    if not isinstance(allowed_paths, (list, tuple)) or not allowed_paths:
        errors.append("invalid_allowed_paths")
    else:
        boundary = build_runtime_boundary()
        prefixes = boundary["allowed_path_prefixes"]
        for path in allowed_paths:
            if not isinstance(path, str) or not path:
                errors.append("invalid_allowed_path_item")
                continue
            if not any(
                path == prefix or path.startswith(prefix)
                for prefix in prefixes
            ):
                errors.append("path_outside_boundary")

    requested = task.get("requested_capabilities")
    if not isinstance(requested, (list, tuple)) or not requested:
        errors.append("invalid_requested_capabilities")

    goal = task.get("goal")
    if not isinstance(goal, str) or not goal.strip():
        errors.append("invalid_goal")

    return {
        "valid": not errors,
        "errors": tuple(dict.fromkeys(errors)),
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
    assert boundary["allowed_branch"] == "research-lab"
    assert boundary["single_task_per_invocation"] is True
    assert boundary["max_repairs_per_cycle"] == 1
    assert boundary["require_ci_green_before_next_task"] is True
    assert boundary["stop_on_human_gate"] is True
    assert boundary["stop_on_policy_violation"] is True
    assert boundary["codex_mcp_connect_authorized"] is False
    assert boundary["codex_process_start_authorized"] is False
    assert boundary["workspace_write_authorized"] is False
    assert boundary["network_execution_authorized"] is False
    assert boundary["secret_access_authorized"] is False
    assert boundary["commerce_authorized"] is False
    assert boundary["production_change_authorized"] is False
    assert boundary["main_branch_change_authorized"] is False
    assert boundary["external_action_authorized"] is False
    return True
