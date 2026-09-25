"""Tests for offline Gemini Orchestrator sandbox pipeline."""

from research_lab.sandbox_gemini_orchestrator_pipeline_design import (
    build_orchestrator_context,
    build_sandbox_gemini_orchestrator_pipeline_design,
    evaluate_fixture_orchestrator_decision,
    validate_sandbox_gemini_orchestrator_pipeline_design,
)


def _record(item_id, price, sale, days, liquidation, confidence=0.9):
    return {
        "provider": "fixture_market",
        "provider_class": "manual_import",
        "item_id": item_id,
        "title": item_id,
        "price_jpy": price,
        "estimated_sale_price_jpy": sale,
        "estimated_fees_jpy": 200,
        "estimated_shipping_jpy": 200,
        "estimated_days_to_sell": days,
        "liquidation_value_jpy": liquidation,
        "market_depth": 0.8,
        "automation_ease": 0.8,
        "confidence": confidence,
        "source_timestamp": "2026-09-25T15:00:00+09:00",
    }


def run_tests():
    assert validate_sandbox_gemini_orchestrator_pipeline_design() is True

    good = _record("used-game-fast", 2600, 4300, 5, 2400, 0.9)
    decision = {
        "decision_type": "rank_candidates",
        "summary": "Use the selected candidate as the current best proposal.",
        "recommended_action": "prepare_executor_request",
        "confidence": 0.86,
        "evidence_refs": ["market_pipeline:selected", "policy:allowed"],
        "requires_human_gate": True,
    }

    result = evaluate_fixture_orchestrator_decision([good], decision)
    assert result["status"] == "ready_for_policy_handoff"
    assert result["decision_validation"]["valid"] is True
    assert result["context"]["selected_item_id"] == "used-game-fast"
    assert result["context"]["reached_human_gate"] is True
    assert result["execution_authorized"] is False
    assert result["commerce_authorized"] is False

    forbidden = dict(decision, recommended_action="purchase_item")
    rejected = evaluate_fixture_orchestrator_decision([good], forbidden)
    assert rejected["status"] == "orchestrator_decision_rejected"
    assert rejected["decision_validation"]["valid"] is False

    bad_market = evaluate_fixture_orchestrator_decision(
        [{"bad": True}],
        decision,
    )
    assert bad_market["status"] == "market_pipeline_not_ready"
    assert bad_market["decision_validation"] is None

    context = build_orchestrator_context(result["market_result"])
    assert context["execution_authorized"] is False
    assert context["commerce_authorized"] is False

    design = build_sandbox_gemini_orchestrator_pipeline_design()
    assert design["gemini_api_call_authorized"] is False
    assert design["secret_access_authorized"] is False
    assert design["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("sandbox Gemini orchestrator pipeline design tests passed")
