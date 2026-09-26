"""Tests for Gemini orchestrator driver design."""

import json

from research_lab.gemini_live_probe import send_assignment_once

from research_lab.gemini_orchestrator_driver_design import (
    build_gemini_orchestrator_driver_design,
    validate_driver_decision,
    validate_gemini_orchestrator_driver_design,
)


def run_tests():
    assignment = {
        "assignment_id": "mile::tick-001::gemini_handoff",
        "milestone_id": "supervisor_connector_live_verification",
        "goal": "Assess the existing research milestone.",
        "constraints": ("no_external_action",),
        "expected_output": ("structured_decision",),
        "escalation_conditions": ("human_gate_required",),
    }
    decision = {
        "schema_version": "0.1", "decision_type": "select_next_theme",
        "summary": "Continue offline research", "recommended_action": "continue_research",
        "confidence": 0.8, "evidence_refs": ["assignment:mile::tick-001::gemini_handoff"],
        "requires_human_gate": False, "risk_flags": [],
    }
    calls = []

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self, _limit=-1):
            return json.dumps({
                "responseId": "gemini-response-001",
                "usageMetadata": {"promptTokenCount": 20, "candidatesTokenCount": 30,
                                  "totalTokenCount": 50},
                "candidates": [{"content": {"parts": [{"text": json.dumps(decision)}]}}],
            }).encode()

    def transport(req, timeout):
        calls.append((req, timeout))
        return Response()

    denied = send_assignment_once(assignment, "run-001", "test-key", lambda: False, transport)
    assert denied["status"] == "blocked"
    assert calls == []

    receipt = send_assignment_once(assignment, "run-001", "test-key", lambda: True, transport)
    assert receipt["status"] == "received"
    assert receipt["decision"] == decision
    assert receipt["assignment_id"] == assignment["assignment_id"]
    assert receipt["source_run_id"] == "run-001"
    assert receipt["provider_response_id"] == "gemini-response-001"
    assert receipt["usage"] == {"input_tokens": 20, "output_tokens": 30, "total_tokens": 50}
    assert receipt["execution_authorized"] is False
    assert "test-key" not in json.dumps(receipt)
    assert len(calls) == 1
    sent = json.loads(calls[0][0].data)
    assert sent["generationConfig"]["maxOutputTokens"] == 512
    assert sent["generationConfig"]["responseMimeType"] == "application/json"
    assert calls[0][1] == 20

    bad = dict(decision, evidence_refs=[])
    decision.clear()
    decision.update(bad)
    rejected = send_assignment_once(assignment, "run-001", "test-key", lambda: True, transport)
    assert rejected["status"] == "rejected_response"

    consumed = False

    def consume_once():
        nonlocal consumed
        if consumed:
            return False
        consumed = True
        return True

    assert send_assignment_once(assignment, "run-001", "test-key", consume_once, transport)["status"] == "rejected_response"
    before_replay = len(calls)
    replay = send_assignment_once(assignment, "run-001", "test-key", consume_once, transport)
    assert replay["status"] == "blocked"
    assert len(calls) == before_replay

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
