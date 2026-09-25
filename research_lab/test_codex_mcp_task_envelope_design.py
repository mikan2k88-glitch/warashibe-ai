"""Tests for Codex MCP task envelope design."""

from research_lab.codex_mcp_task_envelope_design import (
    build_codex_task_envelope,
    build_task_envelope_contract,
    validate_codex_mcp_task_envelope_design,
    validate_codex_task_envelope,
)


def run_tests():
    assert validate_codex_mcp_task_envelope_design() is True

    envelope = build_codex_task_envelope(
        milestone_id="sandbox_external_integration",
        cycle_id="cycle-001",
        task_id="task-001",
        goal="Implement the next missing integration theme.",
        branch="research-lab",
        requested_capabilities=(
            "inspect_repository",
            "edit_code_files",
            "run_offline_tests",
        ),
        acceptance_checks=(
            "offline_tests_green",
            "diff_summary_present",
        ),
    )
    valid = validate_codex_task_envelope(envelope)
    assert valid["valid"] is True
    assert valid["branch"] == "research-lab"
    assert valid["code_write_scope"] == "all_repository_code"
    assert valid["execution_authorized"] is False
    assert valid["requires_codex_runtime_gate"] is True
    assert valid["commit_authorized"] is False

    main_envelope = build_codex_task_envelope(
        milestone_id="core_improvement",
        cycle_id="cycle-002",
        task_id="task-main-001",
        goal="Refactor core code under Orchestrator authorization.",
        branch="main",
        requested_capabilities=(
            "modify_main_branch_code",
            "edit_code_files",
            "run_offline_tests",
        ),
        acceptance_checks=("offline_tests_green",),
    )
    main_valid = validate_codex_task_envelope(main_envelope)
    assert main_valid["valid"] is False
    assert "human_gate_required_for_main_write" in main_valid["errors"]
    main_envelope["human_gate_approved"] = True
    assert validate_codex_task_envelope(main_envelope)["valid"] is True
    assert main_valid["branch"] == "main"

    sensitive = build_codex_task_envelope(
        milestone_id="sensitive",
        cycle_id="cycle-003",
        task_id="task-sensitive-001",
        goal="Attempt sensitive operation.",
        branch="main",
        requested_capabilities=("write_secrets",),
        acceptance_checks=("human_gate_present",),
    )
    blocked = validate_codex_task_envelope(sensitive)
    assert blocked["valid"] is False
    assert "human_gate_required_for_sensitive_action" in blocked["errors"]

    sensitive["human_gate_approved"] = True
    approved_sensitive = validate_codex_task_envelope(sensitive)
    assert approved_sensitive["valid"] is True

    contract = build_task_envelope_contract()
    assert contract["allowed_branches"] == ("research-lab", "main")
    assert contract["main_code_changes_allowed"] is True
    assert contract["main_branch_write_requires_human_gate"] is True
    assert contract["codex_invocation_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Codex MCP task envelope design tests passed")
