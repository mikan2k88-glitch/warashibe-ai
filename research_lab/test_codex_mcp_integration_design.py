"""Tests for Codex MCP integration design."""

from research_lab.codex_mcp_integration_design import (
    build_codex_mcp_lifecycle,
    build_codex_mcp_request_contract,
    validate_codex_mcp_integration_design,
    validate_codex_mcp_task,
)


def _valid_task():
    return {
        "milestone_id": "sandbox_external_integration",
        "cycle_id": "cycle-001",
        "task_id": "task-001",
        "allowed_branch": "research-lab",
        "max_repairs": 1,
        "human_gate_required": True,
        "requested_capabilities": (
            "inspect_repository",
            "edit_research_lab_files",
            "run_offline_tests",
            "report_diff_summary",
        ),
    }


def run_tests():
    assert validate_codex_mcp_integration_design() is True

    contract = build_codex_mcp_request_contract()
    assert contract["allowed_branch"] == "research-lab"
    assert contract["workspace_policy"] == "bounded_workspace_write"
    assert contract["mcp_connection_authorized"] is False
    assert contract["main_branch_change_authorized"] is False

    valid = validate_codex_mcp_task(_valid_task())
    assert valid["valid"] is True
    assert valid["execution_authorized"] is False
    assert valid["requires_live_codex_gate"] is True

    forbidden_task = _valid_task()
    forbidden_task["requested_capabilities"] = ("modify_main_branch",)
    forbidden = validate_codex_mcp_task(forbidden_task)
    assert forbidden["valid"] is False
    assert "forbidden_capability_requested" in forbidden["errors"]

    unknown_task = _valid_task()
    unknown_task["requested_capabilities"] = ("mystery_tool",)
    unknown = validate_codex_mcp_task(unknown_task)
    assert unknown["valid"] is False
    assert "unknown_capability_requested" in unknown["errors"]

    bad_branch = _valid_task()
    bad_branch["allowed_branch"] = "main"
    rejected_branch = validate_codex_mcp_task(bad_branch)
    assert rejected_branch["valid"] is False
    assert "branch_not_allowed" in rejected_branch["errors"]

    lifecycle = build_codex_mcp_lifecycle()
    assert lifecycle["actual_codex_invocation_authorized"] is False
    assert lifecycle["actual_mcp_transport_authorized"] is False
    assert lifecycle["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Codex MCP integration design tests passed")
