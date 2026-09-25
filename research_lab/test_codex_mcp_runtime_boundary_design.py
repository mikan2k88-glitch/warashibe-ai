"""Tests for Codex MCP runtime boundary design."""

from research_lab.codex_mcp_runtime_boundary_design import (
    build_runtime_boundary,
    validate_codex_mcp_runtime_boundary,
    validate_result_envelope,
    validate_runtime_state,
    validate_task_envelope,
)


def _valid_state():
    return {
        "latest_ci_green": True,
        "repository_workspace_ready": True,
        "codex_mcp_server_ready": True,
        "single_task_payload_ready": True,
        "orchestrator_security_ready": True,
        "human_gate_approved": True,
    }


def _valid_task(branch="research-lab"):
    return {
        "milestone_id": "sandbox_external_integration",
        "cycle_id": "cycle-001",
        "task_id": "task-001",
        "goal": "Implement the smallest missing integration theme.",
        "branch": branch,
        "requested_capabilities": (
            "inspect_repository",
            "edit_code_files",
            "run_offline_tests",
        ),
        "max_repairs": 1,
        "orchestrator_authorized": True,
    }


def _valid_result(branch="research-lab"):
    return {
        "task_id": "task-001",
        "status": "completed",
        "branch": branch,
        "changed_files": ["app.py", "research_lab/example.py"],
        "test_command": "python -m research_lab.runner",
        "test_passed": True,
        "diff_summary": "Updated repository code under Orchestrator control.",
        "human_gate_encountered": False,
        "policy_violation_detected": False,
    }


def run_tests():
    assert validate_codex_mcp_runtime_boundary() is True

    state = validate_runtime_state(_valid_state())
    assert state["ready"] is True
    assert state["connect_authorized"] is False
    assert state["requires_one_shot_gate_consumption"] is True

    missing = _valid_state()
    missing["latest_ci_green"] = False
    rejected_state = validate_runtime_state(missing)
    assert rejected_state["ready"] is False
    assert "missing_latest_ci_green" in rejected_state["errors"]

    research_task = validate_task_envelope(_valid_task())
    assert research_task["valid"] is True
    assert research_task["code_write_scope"] == "all_repository_code"

    main_task = validate_task_envelope(_valid_task("main"))
    assert main_task["valid"] is False
    assert "human_gate_required_for_main_write" in main_task["errors"]
    approved_main = _valid_task("main")
    approved_main["human_gate_approved"] = True
    assert validate_task_envelope(approved_main)["valid"] is True

    denied = _valid_task("main")
    denied["orchestrator_authorized"] = False
    rejected_task = validate_task_envelope(denied)
    assert rejected_task["valid"] is False
    assert "orchestrator_authorization_required" in rejected_task["errors"]

    result = validate_result_envelope(_valid_result("main"))
    assert result["valid"] is True
    assert result["safe_to_commit"] is True
    assert result["commit_authorized"] is False

    human_gate = _valid_result()
    human_gate["status"] = "human_gate_required"
    human_gate["human_gate_encountered"] = True
    stopped = validate_result_envelope(human_gate)
    assert stopped["valid"] is True
    assert stopped["safe_to_commit"] is False

    boundary = build_runtime_boundary()
    assert boundary["workspace_scope"] == "entire_repository_codebase"
    assert boundary["allowed_code_branches"] == ("research-lab", "main")
    assert boundary["main_code_changes_allowed"] is True
    assert boundary["security_owner"] == "warashibe_orchestrator"
    assert boundary["codex_mcp_connect_authorized"] is False
    assert boundary["codex_process_start_authorized"] is False
    assert boundary["workspace_write_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Codex MCP runtime boundary design tests passed")
