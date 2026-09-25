"""Canonical result envelope returned from Codex MCP to Warashibe Orchestrator.

The Orchestrator uses this envelope to decide whether a code change may proceed
to commit/CI review. Codex never grants itself commit or branch authority.
"""

from research_lab.codex_orchestrator_security_policy import CODE_BRANCHES

CODEX_MCP_RESULT_ENVELOPE_VERSION = "0.1"

REQUIRED_FIELDS = (
    "envelope_version",
    "milestone_id",
    "cycle_id",
    "task_id",
    "status",
    "branch",
    "changed_files",
    "test_command",
    "test_passed",
    "diff_summary",
    "acceptance_checks",
    "human_gate_encountered",
    "policy_violation_detected",
    "unknown_capability_encountered",
)

ALLOWED_STATUSES = (
    "completed",
    "blocked",
    "failed",
    "human_gate_required",
)

ALLOWED_ACCEPTANCE_STATES = (
    "passed",
    "failed",
    "not_run",
)


def build_codex_result_envelope(
    milestone_id,
    cycle_id,
    task_id,
    status,
    branch,
    changed_files,
    test_command,
    test_passed,
    diff_summary,
    acceptance_checks,
    human_gate_encountered=False,
    policy_violation_detected=False,
    unknown_capability_encountered=False,
):
    return {
        "envelope_version": CODEX_MCP_RESULT_ENVELOPE_VERSION,
        "milestone_id": milestone_id,
        "cycle_id": cycle_id,
        "task_id": task_id,
        "status": status,
        "branch": branch,
        "changed_files": tuple(changed_files or ()),
        "test_command": test_command,
        "test_passed": test_passed,
        "diff_summary": diff_summary,
        "acceptance_checks": dict(acceptance_checks or {}),
        "human_gate_encountered": bool(human_gate_encountered),
        "policy_violation_detected": bool(policy_violation_detected),
        "unknown_capability_encountered": bool(unknown_capability_encountered),
        "commit_authorized": False,
        "main_branch_write_authorized": False,
        "external_action_authorized": False,
    }


def validate_codex_result_envelope(result):
    if not isinstance(result, dict):
        return {
            "valid": False,
            "errors": ("result_not_mapping",),
            "safe_for_orchestrator_commit_review": False,
        }

    errors = []

    for field in REQUIRED_FIELDS:
        if field not in result:
            errors.append(f"missing_{field}")

    if result.get("envelope_version") != CODEX_MCP_RESULT_ENVELOPE_VERSION:
        errors.append("unsupported_envelope_version")

    status = result.get("status")
    if status not in ALLOWED_STATUSES:
        errors.append("unsupported_status")

    branch = result.get("branch")
    if branch not in CODE_BRANCHES:
        errors.append("branch_not_allowed")

    changed_files = result.get("changed_files")
    if not isinstance(changed_files, (list, tuple)):
        errors.append("invalid_changed_files")
    elif not all(isinstance(path, str) and path.strip() for path in changed_files):
        errors.append("invalid_changed_file_item")

    test_command = result.get("test_command")
    if not isinstance(test_command, str) or not test_command.strip():
        errors.append("invalid_test_command")

    if not isinstance(result.get("test_passed"), bool):
        errors.append("invalid_test_passed")

    diff_summary = result.get("diff_summary")
    if not isinstance(diff_summary, str) or not diff_summary.strip():
        errors.append("invalid_diff_summary")

    acceptance_checks = result.get("acceptance_checks")
    if not isinstance(acceptance_checks, dict) or not acceptance_checks:
        errors.append("invalid_acceptance_checks")
    else:
        for name, state in acceptance_checks.items():
            if not isinstance(name, str) or not name.strip():
                errors.append("invalid_acceptance_check_name")
            if state not in ALLOWED_ACCEPTANCE_STATES:
                errors.append("invalid_acceptance_check_state")

    for field in (
        "human_gate_encountered",
        "policy_violation_detected",
        "unknown_capability_encountered",
    ):
        if not isinstance(result.get(field), bool):
            errors.append(f"invalid_{field}")

    acceptance_all_passed = (
        isinstance(acceptance_checks, dict)
        and bool(acceptance_checks)
        and all(state == "passed" for state in acceptance_checks.values())
    )

    safe_for_commit_review = (
        not errors
        and status == "completed"
        and result.get("test_passed") is True
        and acceptance_all_passed
        and result.get("human_gate_encountered") is False
        and result.get("policy_violation_detected") is False
        and result.get("unknown_capability_encountered") is False
    )

    requires_main_write_gate = (
        safe_for_commit_review and branch == "main"
    )

    return {
        "valid": not errors,
        "errors": tuple(dict.fromkeys(errors)),
        "acceptance_all_passed": acceptance_all_passed,
        "safe_for_orchestrator_commit_review": safe_for_commit_review,
        "requires_main_write_gate": requires_main_write_gate,
        "commit_authorized": False,
        "main_branch_write_authorized": False,
    }


def build_result_envelope_contract():
    return {
        "version": CODEX_MCP_RESULT_ENVELOPE_VERSION,
        "mode": "design_only",
        "allowed_branches": CODE_BRANCHES,
        "required_fields": REQUIRED_FIELDS,
        "allowed_statuses": ALLOWED_STATUSES,
        "allowed_acceptance_states": ALLOWED_ACCEPTANCE_STATES,
        "all_acceptance_checks_must_pass": True,
        "tests_must_pass": True,
        "human_gate_must_be_clear": True,
        "policy_violation_must_be_clear": True,
        "unknown_capability_must_be_clear": True,
        "main_branch_write_requires_human_gate": True,
        "codex_self_commit_authorized": False,
        "commit_authorized": False,
        "external_action_authorized": False,
    }


def validate_codex_mcp_result_envelope_design():
    contract = build_result_envelope_contract()
    assert contract["mode"] == "design_only"
    assert contract["allowed_branches"] == ("research-lab", "main")
    assert contract["all_acceptance_checks_must_pass"] is True
    assert contract["tests_must_pass"] is True
    assert contract["human_gate_must_be_clear"] is True
    assert contract["policy_violation_must_be_clear"] is True
    assert contract["unknown_capability_must_be_clear"] is True
    assert contract["main_branch_write_requires_human_gate"] is True
    assert contract["codex_self_commit_authorized"] is False
    assert contract["commit_authorized"] is False
    assert contract["external_action_authorized"] is False
    return True
