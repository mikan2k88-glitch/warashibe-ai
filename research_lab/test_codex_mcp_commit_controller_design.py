"""Tests for Codex MCP commit controller design."""

from research_lab.codex_mcp_commit_controller_design import (
    build_commit_controller_contract,
    decide_commit_action,
    evaluate_main_write_gate,
    validate_codex_mcp_commit_controller_design,
)


def run_tests():
    assert validate_codex_mcp_commit_controller_design() is True

    research_review = {
        "action": "commit_review",
    }
    research = decide_commit_action(
        research_review,
        orchestrator_approved=True,
    )
    assert research["action"] == "prepare_research_lab_commit"
    assert research["commit_authorized"] is False

    main_review = {
        "action": "request_main_write_gate",
    }
    main = decide_commit_action(
        main_review,
        orchestrator_approved=True,
    )
    assert main["action"] == "request_main_write_gate"
    assert main["main_branch_write_authorized"] is False

    denied = decide_commit_action(
        research_review,
        orchestrator_approved=False,
    )
    assert denied["action"] == "stop"
    assert denied["reason"] == "orchestrator_approval_required"

    closed_gate = evaluate_main_write_gate(
        main_review,
        orchestrator_approved=True,
        explicit_human_approval=False,
    )
    assert closed_gate["approved"] is False
    assert "explicit_human_approval_required" in closed_gate["errors"]

    approved_gate = evaluate_main_write_gate(
        main_review,
        orchestrator_approved=True,
        explicit_human_approval=True,
    )
    assert approved_gate["approved"] is True
    assert approved_gate["approval_scope"] == "single_main_branch_write"
    assert approved_gate["approval_reusable"] is False
    assert approved_gate["main_branch_write_authorized"] is True

    contract = build_commit_controller_contract()
    assert contract["security_owner"] == "warashibe_orchestrator"
    assert contract["main_commit_requires_human_gate"] is True
    assert contract["codex_self_commit_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Codex MCP commit controller design tests passed")
