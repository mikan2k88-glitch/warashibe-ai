"""Offline contract tests for one-shot GPT assignment delivery to Gemini.

All transport calls are injected; no API key or external request is used.
"""

import json
from urllib.error import HTTPError

from research_lab.gemini_live_probe import send_assignment_once
from research_lab.gpt_supervisor_schedule_bridge_design import build_gemini_assignment


def assignment():
    state = {
        "schedule_tick_id": "offline-001",
        "milestone_id": "gemini_handoff",
        "current_stage": "offline_test",
        "next_theme": "verify_assignment",
        "latest_ci_green": True,
        "human_gate_pending": False,
    }
    return build_gemini_assignment(state)["assignment"]


def response_for(item, *, valid_ref=True):
    decision = {
        "schema_version": "0.1",
        "decision_type": "select_next_theme",
        "summary": "Analyze only; no execution.",
        "recommended_action": "continue_research",
        "confidence": 0.7,
        "evidence_refs": ["assignment:" + (item["assignment_id"] if valid_ref else "other")],
        "requires_human_gate": False,
        "risk_flags": [],
    }
    return json.dumps({
        "responseId": "offline-response",
        "candidates": [{"content": {"parts": [{"text": json.dumps(decision)}]}}],
        "usageMetadata": {"promptTokenCount": 12, "candidatesTokenCount": 20, "totalTokenCount": 32},
    }).encode()


class FakeResponse:
    status = 200

    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        return self.data[:limit]


def run_tests():
    item = assignment()
    used = set()
    calls = []

    def gate():
        if item["assignment_id"] in used:
            return False
        used.add(item["assignment_id"])
        return True

    def transport(req, timeout):
        calls.append((req, timeout))
        assert timeout == 20
        assert req.get_method() == "POST"
        assert "offline-key" not in req.full_url
        return FakeResponse(response_for(item))

    result = send_assignment_once(item, "source-001", "offline-key", gate, transport)
    assert result["status"] == "received", result
    assert result["provider_response_id"] == "offline-response"
    assert result["usage"]["total_tokens"] == 32
    assert result["execution_authorized"] is False
    assert result["codex_execution_authorized"] is False
    assert len(calls) == 1
    duplicate = send_assignment_once(item, "source-001", "offline-key", gate, transport)
    assert duplicate["status"] == "blocked"
    assert duplicate["reason"] == "one_shot_gate_not_consumed"
    assert len(calls) == 1

    invalid = dict(item)
    invalid["goal"] = ""
    assert send_assignment_once(invalid, "source-002", "offline-key", lambda: True, transport)["status"] == "blocked"
    assert len(calls) == 1

    wrong_ref = send_assignment_once(item, "source-003", "offline-key", lambda: True,
        lambda req, timeout: FakeResponse(response_for(item, valid_ref=False)))
    assert wrong_ref["status"] == "rejected_response"
    assert wrong_ref["reason"] == "invalid_decision"

    malformed = send_assignment_once(item, "source-004", "offline-key", lambda: True,
        lambda req, timeout: FakeResponse(b"not-json"))
    assert malformed["status"] == "rejected_response"

    def http_error(req, timeout):
        raise HTTPError(req.full_url, 503, "offline", {}, None)

    failed = send_assignment_once(item, "source-005", "offline-key", lambda: True, http_error)
    assert failed["status"] == "failed"
    assert failed["http_status"] == 503
    assert failed["execution_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Gemini assignment offline contract tests passed")
