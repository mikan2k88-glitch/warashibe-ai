"""Tests for Gemini orchestrator driver design."""

from research_lab.gemini_orchestrator_driver_design import (
    build_gemini_orchestrator_driver_design,
    validate_driver_decision,
    validate_gemini_orchestrator_driver_design,
)


def run_tests():
    assert validate_gemini_orchestrator_driver_design() is True

    valid = validate_driver_decision({
        "decision_type": "select_next_theme",
        "summary": "Continue candidate scoring research.",
        "recommended_action": "prepare_executor_request",
        "confidence": 0.84,
        "evidence_refs": ["ci:green", "runner:next_theme"],
        "requires_human_gate": False,
    })
    assert valid["valid"] is True
    assert valid["execution_authorized"] is False
    assert valid["requires_policy_validation"] is True

    forbidden = validate_driver_decision({
        "decision_type": "rank_candidates",
        "summary": "Attempt direct purchase.",
        "recommended_action": "purchase_item",
        "confidence": 0.9,
        "evidence_refs": ["candidate:item-001"],
        "requires_human_gate": True,
    })
    assert forbidden["valid"] is False
    assert "forbidden_direct_action" in forbidden["errors"]

    invalid_confidence = validate_driver_decision({
        "decision_type": "analyze_ci_failure",
        "summary": "Bad confidence.",
        "recommended_action": "prepare_executor_request",
        "confidence": 1.5,
        "evidence_refs": [],
        "requires_human_gate": False,
    })
    assert invalid_confidence["valid"] is False

    design = build_gemini_orchestrator_driver_design()
    assert design["model_primary"] == "gemini-3.8-flash"
    assert design["human_gate_preserved"] is True
    assert design["network_execution_authorized"] is False
    assert design["commerce_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("gemini orchestrator driver design tests passed")
