"""Tests for Codex milestone execution gate."""

from research_lab.codex_milestone_execution_gate import (
    build_codex_execution_gate_snapshot,
    evaluate_codex_execution_gate,
    validate_codex_execution_gate,
)


def run_tests():
    assert validate_codex_execution_gate() is True

    closed = evaluate_codex_execution_gate(False)
    assert closed["approved_for_single_codex_invocation"] is False
    assert "explicit_human_approval_required" in closed["blockers"]
    assert closed["approval_reusable"] is False

    approved = evaluate_codex_execution_gate(True)
    assert approved["approved_for_single_codex_invocation"] is True
    assert approved["blockers"] == ()
    assert approved["approval_scope"] == "single_bounded_milestone_execution"
    assert approved["approval_reusable"] is False
    assert approved["allowed_branches"] == ("research-lab", "main")
    assert approved["repository_code_scope"] == "all_repository_code"
    assert approved["network_execution_authorized"] is False
    assert approved["secret_access_authorized"] is False
    assert approved["commerce_authorized"] is False
    assert approved["production_change_authorized"] is False
    assert approved["main_code_changes_allowed"] is True
    assert approved["main_branch_write_requires_human_gate"] is True
    assert approved["main_branch_change_authorized"] is False
    assert approved["live_external_api_authorized"] is False

    snapshot = build_codex_execution_gate_snapshot()
    assert snapshot["mode"] == "awaiting_explicit_human_approval"
    assert snapshot["codex_invocation_authorized"] is False
    assert snapshot["approval_reusable"] is False
    assert snapshot["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Codex milestone execution gate tests passed")
