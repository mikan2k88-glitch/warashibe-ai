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
        "research_lab_branch_confirmed": True,
        "bounded_workspace_ready": True,
        "codex_mcp_server_ready": True,
        "single_task_payload_ready": True,
        "human_gate_approved": True,
    }


def _valid_task():
    return {
        "milestone_id": "sandbox_external_integration",
        "cycle_id": "cycle-001",
        "task_id": "task-001",
        "goal": "Implement the smallest missing sandbox integration theme.",
        "allowed_branch": "research-lab",
        "allowed_paths": (
            "research_lab/example.py",
            "real_world_engine.py",
        ),
        "requested_capabilities": (
            "inspect_repository",
            "edit_research_lab_files",
            "run_offline_tests",
        ),
        "max_repairs": 1,
    }


def _valid_result():
    return {
        "task_id": "task-001",
        "status": "completed",
        "changed_files": ["research_lab/example.py"],
        "test_command": "python -m research_lab.test_example",
        "test_passed": True,
        "diff_summary": "Added bounded sandbox integration.",
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

    task = validate_task_envelope(_valid_task())
    assert task["valid"] is True

    bad_path = _valid_task()
    bad_path["allowed_paths"] = ("app.py",)
    rejected_task = validate_task_envelope(bad_path)
    assert rejected_task["valid"] is False
    assert "path_outside_boundary" in rejected_task["errors"]

    result = validate_result_envelope(_valid_result())
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
    assert boundary["codex_mcp_connect_authorized"] is False
    assert boundary["codex_process_start_authorized"] is False
    assert boundary["workspace_write_authorized"] is False
    assert boundary["main_branch_change_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Codex MCP runtime boundary design tests passed")
