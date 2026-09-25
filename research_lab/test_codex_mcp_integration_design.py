"""Tests for Codex MCP integration design."""

from research_lab.codex_mcp_integration_design import (
    build_codex_mcp_lifecycle,
    build_codex_mcp_request_contract,
    validate_codex_mcp_integration_design,
    validate_codex_mcp_task,
)


def _valid_task(branch="research-lab"):
    return {
        "milestone_id": "sandbox_external_integration",
        "cycle_id": "cycle-001",
        "task_id": "task-001",
        "branch": branch,
        "max_repairs": 1,
        "orchestrator_authorized": True,
        "requested_capabilities": (
            "inspect_repository",
            "edit_code_files",
            "run_offline_tests",
            "report_diff_summary",
        ),
    }


def run_tests():
    assert validate_codex_mcp_integration_design() is True

    contract = build_codex_mcp_request_contract()
    assert contract["allowed_code_branches"] == ("research-lab", "main")
    assert contract["repository_code_scope"] == "all_repository_code"
    assert contract["workspace_policy"] == "repository_wide_code_write"
    assert contract["security_owner"] == "warashibe_orchestrator"
    assert contract["main_code_changes_allowed"] is True

    valid = validate_codex_mcp_task(_valid_task())
    assert valid["valid"] is True
    assert valid["execution_authorized"] is False
    assert valid["requires_live_codex_gate"] is True

    main = validate_codex_mcp_task(_valid_task("main"))
    assert main["valid"] is False
    assert "human_gate_required_for_main_write" in main["errors"]
    approved_main = _valid_task("main")
    approved_main["human_gate_approved"] = True
    assert validate_codex_mcp_task(approved_main)["valid"] is True

    denied = _valid_task("main")
    denied["orchestrator_authorized"] = False
    rejected = validate_codex_mcp_task(denied)
    assert rejected["valid"] is False
    assert "orchestrator_authorization_required" in rejected["errors"]

    sensitive = _valid_task("main")
    sensitive["requested_capabilities"] = ("write_secrets",)
    blocked = validate_codex_mcp_task(sensitive)
    assert blocked["valid"] is False
    assert "human_gate_required_for_sensitive_action" in blocked["errors"]

    lifecycle = build_codex_mcp_lifecycle()
    assert lifecycle["actual_codex_invocation_authorized"] is False
    assert lifecycle["actual_mcp_transport_authorized"] is False
    assert lifecycle["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Codex MCP integration design tests passed")
