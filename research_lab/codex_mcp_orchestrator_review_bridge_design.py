"""Bridge Codex result envelopes into deterministic Orchestrator decisions.

The bridge never commits code itself. It decides whether the Orchestrator should
proceed to commit review, request one repair, stop, or request a HUMAN GATE.
"""

from research_lab.codex_mcp_result_envelope_design import (
    validate_codex_result_envelope,
)

CODEX_MCP_ORCHESTRATOR_REVIEW_BRIDGE_VERSION = "0.1"

ACTIONS = (
    "commit_review",
    "repair_once",
    "stop",
    "request_human_gate",
    "request_main_write_gate",
)


def review_codex_result(result, repairs_used=0):
    validation = validate_codex_result_envelope(result)

    if not validation.get("valid"):
        return {
            "version": CODEX_MCP_ORCHESTRATOR_REVIEW_BRIDGE_VERSION,
            "action": "stop",
            "reason": "invalid_result_envelope",
            "validation": validation,
            "commit_authorized": False,
            "external_action_authorized": False,
        }

    if result.get("human_gate_encountered") is True:
        return {
            "version": CODEX_MCP_ORCHESTRATOR_REVIEW_BRIDGE_VERSION,
            "action": "request_human_gate",
            "reason": "codex_reported_human_gate",
            "validation": validation,
            "commit_authorized": False,
            "external_action_authorized": False,
        }

    if (
        result.get("policy_violation_detected") is True
        or result.get("unknown_capability_encountered") is True
    ):
        return {
            "version": CODEX_MCP_ORCHESTRATOR_REVIEW_BRIDGE_VERSION,
            "action": "stop",
            "reason": "policy_or_unknown_capability",
            "validation": validation,
            "commit_authorized": False,
            "external_action_authorized": False,
        }

    if validation.get("safe_for_orchestrator_commit_review") is True:
        if validation.get("requires_main_write_gate") is True:
            return {
                "version": CODEX_MCP_ORCHESTRATOR_REVIEW_BRIDGE_VERSION,
                "action": "request_main_write_gate",
                "reason": "main_branch_write_requires_human_gate",
                "validation": validation,
                "commit_authorized": False,
                "main_branch_write_authorized": False,
                "external_action_authorized": False,
            }

        return {
            "version": CODEX_MCP_ORCHESTRATOR_REVIEW_BRIDGE_VERSION,
            "action": "commit_review",
            "reason": "result_ready_for_orchestrator_commit_review",
            "validation": validation,
            "commit_authorized": False,
            "external_action_authorized": False,
        }

    if repairs_used < 1 and result.get("status") in ("failed", "blocked"):
        return {
            "version": CODEX_MCP_ORCHESTRATOR_REVIEW_BRIDGE_VERSION,
            "action": "repair_once",
            "reason": "single_repair_available",
            "validation": validation,
            "next_repairs_used": repairs_used + 1,
            "commit_authorized": False,
            "external_action_authorized": False,
        }

    return {
        "version": CODEX_MCP_ORCHESTRATOR_REVIEW_BRIDGE_VERSION,
        "action": "stop",
        "reason": "result_not_safe_and_no_repair_path",
        "validation": validation,
        "commit_authorized": False,
        "external_action_authorized": False,
    }


def build_orchestrator_review_bridge_contract():
    return {
        "version": CODEX_MCP_ORCHESTRATOR_REVIEW_BRIDGE_VERSION,
        "mode": "design_only",
        "actions": ACTIONS,
        "max_repairs": 1,
        "research_lab_success_action": "commit_review",
        "main_success_action": "request_main_write_gate",
        "human_gate_action": "request_human_gate",
        "policy_violation_action": "stop",
        "unknown_capability_action": "stop",
        "codex_self_commit_authorized": False,
        "orchestrator_commit_authorized": False,
        "main_branch_write_authorized": False,
        "external_action_authorized": False,
    }


def validate_codex_mcp_orchestrator_review_bridge_design():
    contract = build_orchestrator_review_bridge_contract()
    assert contract["mode"] == "design_only"
    assert contract["max_repairs"] == 1
    assert contract["research_lab_success_action"] == "commit_review"
    assert contract["main_success_action"] == "request_main_write_gate"
    assert contract["human_gate_action"] == "request_human_gate"
    assert contract["policy_violation_action"] == "stop"
    assert contract["unknown_capability_action"] == "stop"
    assert contract["codex_self_commit_authorized"] is False
    assert contract["orchestrator_commit_authorized"] is False
    assert contract["main_branch_write_authorized"] is False
    assert contract["external_action_authorized"] is False
    return True
