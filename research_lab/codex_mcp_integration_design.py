"""Design the Warashibe Orchestrator -> Codex MCP integration.

This module defines a bounded integration contract only. It does not start
Codex, open a network connection, read secrets, or execute external commands.
"""

CODEX_MCP_INTEGRATION_DESIGN_VERSION = "0.1"

ARCHITECTURE = (
    "warashibe_orchestrator",
    "codex_mcp_server",
    "bounded_workspace",
    "research_lab_branch",
    "offline_tests",
    "github_push",
    "ci_verification",
    "orchestrator_review",
)

ALLOWED_CODEX_CAPABILITIES = (
    "inspect_repository",
    "edit_research_lab_files",
    "create_research_lab_files",
    "run_offline_tests",
    "prepare_commit",
    "report_diff_summary",
    "report_test_results",
)

FORBIDDEN_CODEX_CAPABILITIES = (
    "modify_main_branch",
    "modify_production_configuration",
    "read_secrets",
    "write_secrets",
    "purchase_item",
    "list_item",
    "send_payment",
    "issue_refund",
    "write_production_database",
    "invoke_live_gemini",
    "invoke_live_stripe",
    "invoke_unbounded_external_tools",
)

REQUIRED_CONTROL_FIELDS = (
    "milestone_id",
    "cycle_id",
    "task_id",
    "allowed_branch",
    "max_repairs",
    "human_gate_required",
)


def build_codex_mcp_request_contract():
    return {
        "version": CODEX_MCP_INTEGRATION_DESIGN_VERSION,
        "mode": "design_only",
        "transport": "mcp",
        "architecture": ARCHITECTURE,
        "allowed_capabilities": ALLOWED_CODEX_CAPABILITIES,
        "forbidden_capabilities": FORBIDDEN_CODEX_CAPABILITIES,
        "required_control_fields": REQUIRED_CONTROL_FIELDS,
        "allowed_branch": "research-lab",
        "workspace_policy": "bounded_workspace_write",
        "one_theme_per_request": True,
        "max_repairs_per_cycle": 1,
        "require_offline_tests_before_commit": True,
        "require_ci_green_before_next_request": True,
        "stop_on_human_gate": True,
        "stop_on_unknown_capability": True,
        "stop_on_policy_violation": True,
        "network_default": "deny",
        "secret_default": "deny",
        "commerce_default": "deny",
        "codex_process_start_authorized": False,
        "mcp_connection_authorized": False,
        "network_execution_authorized": False,
        "secret_access_authorized": False,
        "commerce_authorized": False,
        "production_change_authorized": False,
        "main_branch_change_authorized": False,
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

    if task.get("allowed_branch") != "research-lab":
        errors.append("branch_not_allowed")

    requested = tuple(task.get("requested_capabilities") or ())
    forbidden = tuple(
        capability
        for capability in requested
        if capability in FORBIDDEN_CODEX_CAPABILITIES
    )
    unknown = tuple(
        capability
        for capability in requested
        if capability not in ALLOWED_CODEX_CAPABILITIES
        and capability not in FORBIDDEN_CODEX_CAPABILITIES
    )

    if forbidden:
        errors.append("forbidden_capability_requested")
    if unknown:
        errors.append("unknown_capability_requested")

    if task.get("max_repairs") != 1:
        errors.append("invalid_max_repairs")

    if task.get("human_gate_required") is not True:
        errors.append("human_gate_must_remain_enabled")

    return {
        "valid": not errors,
        "errors": tuple(errors),
        "forbidden_capabilities": forbidden,
        "unknown_capabilities": unknown,
        "execution_authorized": False,
        "requires_live_codex_gate": True,
    }


def build_codex_mcp_lifecycle():
    return {
        "version": CODEX_MCP_INTEGRATION_DESIGN_VERSION,
        "flow": (
            "orchestrator_selects_smallest_missing_theme",
            "build_bounded_codex_task",
            "validate_task_contract",
            "request_live_codex_gate",
            "send_single_task_over_mcp",
            "codex_edits_bounded_workspace",
            "codex_runs_offline_tests",
            "codex_returns_diff_and_test_report",
            "orchestrator_reviews_result",
            "commit_research_lab_only",
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
    assert contract["allowed_branch"] == "research-lab"
    assert contract["one_theme_per_request"] is True
    assert contract["max_repairs_per_cycle"] == 1
    assert contract["require_offline_tests_before_commit"] is True
    assert contract["require_ci_green_before_next_request"] is True
    assert contract["stop_on_human_gate"] is True
    assert contract["network_default"] == "deny"
    assert contract["secret_default"] == "deny"
    assert contract["commerce_default"] == "deny"
    assert contract["codex_process_start_authorized"] is False
    assert contract["mcp_connection_authorized"] is False
    assert contract["network_execution_authorized"] is False
    assert contract["secret_access_authorized"] is False
    assert contract["commerce_authorized"] is False
    assert contract["production_change_authorized"] is False
    assert contract["main_branch_change_authorized"] is False
    assert contract["external_action_authorized"] is False
    return True
