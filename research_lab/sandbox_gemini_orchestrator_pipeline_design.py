"""Offline Gemini Orchestrator pipeline design for Warashibe AI sandbox.

This module connects market-candidate pipeline results to the Gemini
Orchestrator Driver contract without calling Gemini. It validates a fixture
structured decision and keeps execution authority outside the model boundary.
"""

from research_lab.gemini_orchestrator_driver_design import (
    validate_driver_decision,
)
from research_lab.sandbox_market_candidate_pipeline import (
    run_sandbox_market_candidate_pipeline,
)

SANDBOX_GEMINI_ORCHESTRATOR_PIPELINE_VERSION = "0.1"


def build_orchestrator_context(market_pipeline_result):
    selection = (market_pipeline_result or {}).get("selection") or {}
    candidate = selection.get("candidate") or {}
    scoring = selection.get("scoring") or {}
    route = selection.get("route") or {}

    return {
        "market_status": (market_pipeline_result or {}).get("status"),
        "reached_human_gate": (market_pipeline_result or {}).get(
            "reached_human_gate",
            False,
        ),
        "selected_item_id": candidate.get("item_id"),
        "selected_title": candidate.get("title") or candidate.get("name"),
        "candidate_score": scoring.get("score"),
        "expected_net_profit_jpy": scoring.get("expected_net_profit_jpy"),
        "maximum_expected_loss_jpy": scoring.get("maximum_expected_loss_jpy"),
        "profit_per_day_jpy": scoring.get("profit_per_day_jpy"),
        "recovery_rate": scoring.get("recovery_rate"),
        "route_status": route.get("status"),
        "route_data_complete": route.get("route_data_complete", False),
        "execution_authorized": False,
        "commerce_authorized": False,
    }


def evaluate_fixture_orchestrator_decision(
    market_records,
    decision_payload,
    route_ladder=None,
    target_jpy=1_000_000,
):
    market_result = run_sandbox_market_candidate_pipeline(
        market_records,
        route_ladder=route_ladder,
        target_jpy=target_jpy,
    )
    context = build_orchestrator_context(market_result)

    if not market_result.get("reached_human_gate"):
        return {
            "version": SANDBOX_GEMINI_ORCHESTRATOR_PIPELINE_VERSION,
            "mode": "offline_fixture_orchestrator_pipeline",
            "status": "market_pipeline_not_ready",
            "market_result": market_result,
            "context": context,
            "decision_validation": None,
            "execution_authorized": False,
            "commerce_authorized": False,
            "external_action_authorized": False,
        }

    validation = validate_driver_decision(decision_payload)
    return {
        "version": SANDBOX_GEMINI_ORCHESTRATOR_PIPELINE_VERSION,
        "mode": "offline_fixture_orchestrator_pipeline",
        "status": (
            "ready_for_policy_handoff"
            if validation.get("valid")
            else "orchestrator_decision_rejected"
        ),
        "market_result": market_result,
        "context": context,
        "decision_validation": validation,
        "execution_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
    }


def build_sandbox_gemini_orchestrator_pipeline_design():
    return {
        "version": SANDBOX_GEMINI_ORCHESTRATOR_PIPELINE_VERSION,
        "mode": "design_only",
        "model_role": "reasoning_driver_only",
        "structured_decision_required": True,
        "market_context_required": True,
        "policy_handoff_required": True,
        "bounded_executor_required": True,
        "human_gate_preserved": True,
        "network_execution_authorized": False,
        "gemini_api_call_authorized": False,
        "secret_access_authorized": False,
        "purchase_authorized": False,
        "listing_authorized": False,
        "payment_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
        "flow": (
            "run_market_candidate_pipeline",
            "build_bounded_orchestrator_context",
            "receive_fixture_structured_decision",
            "validate_driver_schema",
            "handoff_to_policy_boundary",
            "stop_before_executor",
        ),
    }


def validate_sandbox_gemini_orchestrator_pipeline_design():
    design = build_sandbox_gemini_orchestrator_pipeline_design()
    assert design["model_role"] == "reasoning_driver_only"
    assert design["structured_decision_required"] is True
    assert design["market_context_required"] is True
    assert design["policy_handoff_required"] is True
    assert design["bounded_executor_required"] is True
    assert design["human_gate_preserved"] is True
    assert design["network_execution_authorized"] is False
    assert design["gemini_api_call_authorized"] is False
    assert design["secret_access_authorized"] is False
    assert design["commerce_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
