"""Tests for Gemini structured output schema design."""

from research_lab.sandbox_gemini_structured_output_schema_design import (
    SANDBOX_GEMINI_STRUCTURED_OUTPUT_SCHEMA_VERSION,
    build_schema_contract,
    validate_structured_output,
)


def run_tests():
    valid_payload = {
        "schema_version": SANDBOX_GEMINI_STRUCTURED_OUTPUT_SCHEMA_VERSION,
        "decision_type": "rank_candidates",
        "summary": "Candidate A is the strongest current proposal.",
        "recommended_action": "prepare_human_gate",
        "confidence": 0.88,
        "evidence_refs": ["market:selected", "policy:allowed"],
        "requires_human_gate": True,
        "risk_flags": ["route_data_incomplete"],
    }
    valid = validate_structured_output(valid_payload)
    assert valid["valid"] is True
    assert valid["execution_authorized"] is False
    assert valid["commerce_authorized"] is False
    assert valid["requires_policy_validation"] is True

    bad_action = dict(valid_payload, recommended_action="purchase_item")
    rejected_action = validate_structured_output(bad_action)
    assert rejected_action["valid"] is False
    assert "unsupported_recommended_action" in rejected_action["errors"]

    bad_confidence = dict(valid_payload, confidence=1.5)
    rejected_confidence = validate_structured_output(bad_confidence)
    assert rejected_confidence["valid"] is False
    assert "confidence_out_of_range" in rejected_confidence["errors"]

    missing = dict(valid_payload)
    missing.pop("evidence_refs")
    rejected_missing = validate_structured_output(missing)
    assert rejected_missing["valid"] is False
    assert "missing_evidence_refs" in rejected_missing["errors"]

    contract = build_schema_contract()
    assert contract["additional_fields_allowed"] is False
    assert contract["policy_validation_required"] is True
    assert contract["bounded_executor_required"] is True
    assert contract["network_execution_authorized"] is False
    assert contract["gemini_api_call_authorized"] is False
    assert contract["commerce_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("sandbox Gemini structured output schema design tests passed")
