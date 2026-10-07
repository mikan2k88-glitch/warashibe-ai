import json

from research_lab import gemini_live_probe


DEPRECATED_GENERATION_PARAMETERS = {
    "thinking_budget",
    "temperature",
    "top_p",
    "top_k",
}


class _FakeResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(
            {
                "candidates": [
                    {"content": {"parts": [{"text": "WARASHIBE_GEMINI_OK"}]}}
                ]
            }
        ).encode("utf-8")


def test_live_probe_request_omits_deprecated_generation_parameters(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout):
        captured["payload"] = json.loads(req.data.decode("utf-8"))
        return _FakeResponse()

    monkeypatch.setattr(gemini_live_probe.request, "urlopen", fake_urlopen)

    ok, status, detail = gemini_live_probe._call_model(
        "test-api-key",
        gemini_live_probe.PRIMARY_MODEL,
    )

    assert ok is True
    assert status == 200
    assert detail == "WARASHIBE_GEMINI_OK"

    generation_config = captured["payload"].get("generationConfig", {})
    assert DEPRECATED_GENERATION_PARAMETERS.isdisjoint(generation_config)


def test_assignment_request_omits_deprecated_generation_parameters():
    source = gemini_live_probe.send_assignment_once.__code__.co_consts
    serialized = repr(source)

    for parameter in DEPRECATED_GENERATION_PARAMETERS:
        assert parameter not in serialized
