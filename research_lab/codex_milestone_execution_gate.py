"""One-shot HUMAN GATE immediately before real Codex milestone execution.

This module does not invoke Codex. It evaluates whether an explicit human
approval may be consumed for exactly one bounded milestone execution.
"""

from research_lab.codex_milestone_activation_review import (
    run_codex_milestone_activation_review,
)
from research_lab.codex_milestone_executor_design import (
    build_codex_milestone_contract,
)

CODEX_MILESTONE_EXECUTION_GATE_VERSION = "0.1"


def evaluate_codex_execution_gate(explicit_human_approval=False):
    review = run_codex_milestone_activation_review()
    contract = build_codex_milestone_contract()

    blockers = list(review.get("blockers", ()))

    if review.get("ready_for_human_gate") is not True:
        blockers.append("activation_review_not_ready")

    if explicit_human_approval is not True:
        blockers.append("explicit_human_approval_required")

    safe_contract = (
        contract.get("allowed_branches") == ("research-lab",)
        and contract["execution_limits"].get("max_cycles") == 10
        and contract["execution_limits"].get("max_repairs_per_cycle") == 1
        and contract["execution_limits"].get("stop_on_human_gate") is True
        and contract.get("network_execution_authorized") is False
        and contract.get("secret_access_authorized") is False
        and contract.get("commerce_authorized") is False
        and contract.get("production_change_authorized") is False
        and contract.get("main_branch_change_authorized") is False
    )
    if not safe_contract:
        blockers.append("unsafe_codex_contract")

    approved = not blockers

    return {
        "version": CODEX_MILESTONE_EXECUTION_GATE_VERSION,
        "mode": "one_shot_human_gate",
        "milestone_id": contract["milestone_id"],
        "approved_for_single_codex_invocation": approved,
        "blockers": tuple(dict.fromkeys(blockers)),
        "approval_scope": (
            "single_bounded_milestone_execution"
            if approved
            else None
        ),
        "approval_reusable": False,
        "allowed_branch": "research-lab",
        "max_cycles": 10,
        "max_repairs_per_cycle": 1,
        "network_execution_authorized": False,
        "secret_access_authorized": False,
        "commerce_authorized": False,
        "production_change_authorized": False,
        "main_branch_change_authorized": False,
        "live_external_api_authorized": False,
    }


def build_codex_execution_gate_snapshot():
    closed = evaluate_codex_execution_gate(False)
    return {
        "version": CODEX_MILESTONE_EXECUTION_GATE_VERSION,
        "mode": "awaiting_explicit_human_approval",
        "closed_gate": closed,
        "next_required_action": "obtain_explicit_human_approval",
        "codex_invocation_authorized": False,
        "approval_reusable": False,
        "external_action_authorized": False,
    }


def validate_codex_execution_gate():
    closed = evaluate_codex_execution_gate(False)
    assert closed["approved_for_single_codex_invocation"] is False
    assert "explicit_human_approval_required" in closed["blockers"]
    assert closed["approval_reusable"] is False
    assert closed["allowed_branch"] == "research-lab"
    assert closed["max_cycles"] == 10
    assert closed["max_repairs_per_cycle"] == 1
    assert closed["network_execution_authorized"] is False
    assert closed["secret_access_authorized"] is False
    assert closed["commerce_authorized"] is False
    assert closed["production_change_authorized"] is False
    assert closed["main_branch_change_authorized"] is False
    assert closed["live_external_api_authorized"] is False
    return True
