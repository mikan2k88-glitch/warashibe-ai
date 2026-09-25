"""Commit controller for Codex results under GPT/Gemini supervision.

This layer decides whether an already-reviewed Codex result may proceed to a
Git commit. It does not commit anything itself.
"""

CODEX_MCP_COMMIT_CONTROLLER_VERSION = "0.1"

ALLOWED_ACTIONS = (
    "prepare_research_lab_commit",
    "request_main_write_gate",
    "stop",
)


def decide_commit_action(review_bridge_result, orchestrator_approved=False):
    if not isinstance(review_bridge_result, dict):
        return {
            "action": "stop",
            "reason": "invalid_review_result",
            "commit_authorized": False,
        }

    if orchestrator_approved is not True:
        return {
            "action": "stop",
            "reason": "orchestrator_approval_required",
            "commit_authorized": False,
        }

    action = review_bridge_result.get("action")

    if action == "commit_review":
        return {
            "version": CODEX_MCP_COMMIT_CONTROLLER_VERSION,
            "action": "prepare_research_lab_commit",
            "reason": "research_lab_result_approved",
            "commit_authorized": False,
            "main_branch_write_authorized": False,
            "external_action_authorized": False,
        }

    if action == "request_main_write_gate":
        return {
            "version": CODEX_MCP_COMMIT_CONTROLLER_VERSION,
            "action": "request_main_write_gate",
            "reason": "main_requires_human_gate",
            "commit_authorized": False,
            "main_branch_write_authorized": False,
            "external_action_authorized": False,
        }

    return {
        "version": CODEX_MCP_COMMIT_CONTROLLER_VERSION,
        "action": "stop",
        "reason": "review_bridge_did_not_approve_commit_path",
        "commit_authorized": False,
        "main_branch_write_authorized": False,
        "external_action_authorized": False,
    }


def evaluate_main_write_gate(
    review_bridge_result,
    orchestrator_approved=False,
    explicit_human_approval=False,
):
    if not isinstance(review_bridge_result, dict):
        return {
            "approved": False,
            "errors": ("invalid_review_result",),
            "main_branch_write_authorized": False,
        }

    errors = []

    if review_bridge_result.get("action") != "request_main_write_gate":
        errors.append("main_write_gate_not_requested")

    if orchestrator_approved is not True:
        errors.append("orchestrator_approval_required")

    if explicit_human_approval is not True:
        errors.append("explicit_human_approval_required")

    approved = not errors

    return {
        "version": CODEX_MCP_COMMIT_CONTROLLER_VERSION,
        "approved": approved,
        "errors": tuple(errors),
        "approval_scope": "single_main_branch_write" if approved else None,
        "approval_reusable": False,
        "main_branch_write_authorized": approved,
        "external_action_authorized": False,
    }


def build_commit_controller_contract():
    return {
        "version": CODEX_MCP_COMMIT_CONTROLLER_VERSION,
        "mode": "design_only",
        "allowed_actions": ALLOWED_ACTIONS,
        "security_owner": "warashibe_orchestrator",
        "research_lab_commit_requires_orchestrator_approval": True,
        "main_commit_requires_orchestrator_approval": True,
        "main_commit_requires_human_gate": True,
        "codex_self_commit_authorized": False,
        "orchestrator_commit_authorized": False,
        "main_branch_write_authorized": False,
        "external_action_authorized": False,
    }


def validate_codex_mcp_commit_controller_design():
    contract = build_commit_controller_contract()
    assert contract["mode"] == "design_only"
    assert contract["security_owner"] == "warashibe_orchestrator"
    assert contract["research_lab_commit_requires_orchestrator_approval"] is True
    assert contract["main_commit_requires_orchestrator_approval"] is True
    assert contract["main_commit_requires_human_gate"] is True
    assert contract["codex_self_commit_authorized"] is False
    assert contract["orchestrator_commit_authorized"] is False
    assert contract["main_branch_write_authorized"] is False
    assert contract["external_action_authorized"] is False
    return True
