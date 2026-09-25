"""Tests for Codex MCP result envelope design."""

from research_lab.codex_mcp_result_envelope_design import (
    build_codex_result_envelope,
    build_result_envelope_contract,
    validate_codex_mcp_result_envelope_design,
    validate_codex_result_envelope,
)


def _result(branch="research-lab"):
    return build_codex_result_envelope(
        milestone_id="sandbox_external_integration",
        cycle_id="cycle-001",
        task_id="task-001",
        status="completed",
        branch=branch,
        changed_files=("app.py", "research_lab/example.py"),
        test_command="python -m research_lab.runner",
        test_passed=True,
        diff_summary="Implemented the bounded integration theme.",
        acceptance_checks={
            "offline_tests_green": "passed",
            "diff_summary_present": "passed",
        },
    )


def run_tests():
    assert validate_codex_mcp_result_envelope_design() is True

    research = validate_codex_result_envelope(_result())
    assert research["valid"] is True
    assert research["acceptance_all_passed"] is True
    assert research["safe_for_orchestrator_commit_review"] is True
    assert research["requires_main_write_gate"] is False
    assert research["commit_authorized"] is False

    main = validate_codex_result_envelope(_result("main"))
    assert main["valid"] is True
    assert main["safe_for_orchestrator_commit_review"] is True
    assert main["requires_main_write_gate"] is True
    assert main["main_branch_write_authorized"] is False

    failed_check = _result()
    failed_check["acceptance_checks"]["offline_tests_green"] = "failed"
    rejected_check = validate_codex_result_envelope(failed_check)
    assert rejected_check["valid"] is True
    assert rejected_check["acceptance_all_passed"] is False
    assert rejected_check["safe_for_orchestrator_commit_review"] is False

    policy_violation = _result()
    policy_violation["policy_violation_detected"] = True
    rejected_policy = validate_codex_result_envelope(policy_violation)
    assert rejected_policy["valid"] is True
    assert rejected_policy["safe_for_orchestrator_commit_review"] is False

    human_gate = _result()
    human_gate["status"] = "human_gate_required"
    human_gate["human_gate_encountered"] = True
    stopped = validate_codex_result_envelope(human_gate)
    assert stopped["valid"] is True
    assert stopped["safe_for_orchestrator_commit_review"] is False

    contract = build_result_envelope_contract()
    assert contract["allowed_branches"] == ("research-lab", "main")
    assert contract["main_branch_write_requires_human_gate"] is True
    assert contract["codex_self_commit_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Codex MCP result envelope design tests passed")
