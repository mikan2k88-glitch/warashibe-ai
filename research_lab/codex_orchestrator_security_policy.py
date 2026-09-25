"""Central security policy for Codex execution under Warashibe Orchestrator.

Codex may modify any repository code, including main, only when a task has
explicit Orchestrator authorization. Non-code sensitive actions remain gated.
This module does not invoke Codex or modify main by itself.
"""

CODEX_ORCHESTRATOR_SECURITY_POLICY_VERSION = "0.1"

CODE_BRANCHES = ("research-lab", "main")
REPOSITORY_CODE_SCOPE = "all_repository_code"

CODE_CAPABILITIES = (
    "inspect_repository",
    "create_code_files",
    "edit_code_files",
    "delete_code_files",
    "refactor_code",
    "modify_tests",
    "modify_ci_code",
    "modify_main_branch_code",
    "run_offline_tests",
    "prepare_commit",
    "report_diff_summary",
    "report_test_results",
)

SENSITIVE_NON_CODE_CAPABILITIES = (
    "read_secrets",
    "write_secrets",
    "modify_production_configuration",
    "purchase_item",
    "list_item",
    "send_payment",
    "issue_refund",
    "write_production_database",
    "invoke_live_gemini",
    "invoke_live_stripe",
    "invoke_unbounded_external_tools",
)


def build_orchestrator_security_policy():
    return {
        "version": CODEX_ORCHESTRATOR_SECURITY_POLICY_VERSION,
        "security_owner": "warashibe_orchestrator",
        "repository_code_scope": REPOSITORY_CODE_SCOPE,
        "allowed_code_branches": CODE_BRANCHES,
        "allowed_code_capabilities": CODE_CAPABILITIES,
        "sensitive_non_code_capabilities": SENSITIVE_NON_CODE_CAPABILITIES,
        "all_code_changes_require_orchestrator_authorization": True,
        "main_code_changes_allowed": True,
        "main_code_changes_require_orchestrator_authorization": True,
        "sensitive_non_code_actions_require_human_gate": True,
        "unknown_capabilities_default": "deny",
        "codex_self_escalation_allowed": False,
        "codex_policy_override_allowed": False,
        "external_action_authorized": False,
    }


def validate_orchestrator_code_task(task):
    if not isinstance(task, dict):
        return {"valid": False, "errors": ("task_not_mapping",)}

    errors = []

    if task.get("orchestrator_authorized") is not True:
        errors.append("orchestrator_authorization_required")

    if task.get("branch") not in CODE_BRANCHES:
        errors.append("branch_not_allowed")

    requested = tuple(task.get("requested_capabilities") or ())
    sensitive = tuple(
        item for item in requested if item in SENSITIVE_NON_CODE_CAPABILITIES
    )
    unknown = tuple(
        item for item in requested
        if item not in CODE_CAPABILITIES
        and item not in SENSITIVE_NON_CODE_CAPABILITIES
    )

    if sensitive and task.get("human_gate_approved") is not True:
        errors.append("human_gate_required_for_sensitive_action")
    if unknown:
        errors.append("unknown_capability_requested")

    return {
        "valid": not errors,
        "errors": tuple(errors),
        "sensitive_capabilities": sensitive,
        "unknown_capabilities": unknown,
        "code_write_scope": REPOSITORY_CODE_SCOPE,
    }


def validate_codex_orchestrator_security_policy():
    policy = build_orchestrator_security_policy()
    assert policy["security_owner"] == "warashibe_orchestrator"
    assert policy["repository_code_scope"] == "all_repository_code"
    assert policy["allowed_code_branches"] == ("research-lab", "main")
    assert policy["main_code_changes_allowed"] is True
    assert policy["main_code_changes_require_orchestrator_authorization"] is True
    assert policy["sensitive_non_code_actions_require_human_gate"] is True
    assert policy["codex_self_escalation_allowed"] is False
    assert policy["codex_policy_override_allowed"] is False
    return True
