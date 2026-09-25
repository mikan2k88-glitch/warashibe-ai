"""Tests for Codex MCP orchestrator review bridge design."""

from research_lab.codex_mcp_orchestrator_review_bridge_design import (
    build_orchestrator_review_bridge_contract,
    review_codex_result,
    validate_codex_mcp_orchestrator_review_bridge_design,
)
from research_lab.codex_mcp_result_envelope_design import (
    build_codex_result_envelope,
)


def _result(branch="research-lab", status="completed", test_passed=True):
    return build_codex_result_envelope(
        milestone_id="sandbox_external_integration",
        cycle_id="cycle-001",
        task_id="task-001",
        status=status,
        branch=branch,
        changed_files=("app.py",),
        test_command="python -m research_lab.runner",
        test_passed=test_passed,
        diff_summary="Codex completed the requested code change.",
        acceptance_checks={"offline_tests_green": "passed" if test_passed else "failed"},
    )


def run_tests():
    assert validate_codex_mcp_orchestrator_review_bridge_design() is True

    research = review_codex_result(_result())
    assert research["action"] == "commit_review"
    assert research["commit_authorized"] is False

    main = review_codex_result(_result("main"))
    assert main["action"] == "request_main_write_gate"
    assert main["main_branch_write_authorized"] is False

    failed = review_codex_result(_result(status="failed", test_passed=False))
    assert failed["action"] == "repair_once"
    assert failed["next_repairs_used"] == 1

    failed_again = review_codex_result(
        _result(status="failed", test_passed=False),
        repairs_used=1,
    )
    assert failed_again["action"] == "stop"

    human_gate_result = _result()
    human_gate_result["status"] = "human_gate_required"
    human_gate_result["human_gate_encountered"] = True
    human_gate = review_codex_result(human_gate_result)
    assert human_gate["action"] == "request_human_gate"

    policy_result = _result()
    policy_result["policy_violation_detected"] = True
    policy = review_codex_result(policy_result)
    assert policy["action"] == "stop"

    unknown_result = _result()
    unknown_result["unknown_capability_encountered"] = True
    unknown = review_codex_result(unknown_result)
    assert unknown["action"] == "stop"

    contract = build_orchestrator_review_bridge_contract()
    assert contract["main_success_action"] == "request_main_write_gate"
    assert contract["max_repairs"] == 1
    assert contract["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Codex MCP orchestrator review bridge design tests passed")
