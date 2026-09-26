"""Offline tests for the Gemini connectivity probe fallback policy.

No network access or API key is required. This does not validate live model
availability or the separate GPT assignment handoff.
"""

from unittest.mock import patch

from research_lab import gemini_live_probe as probe


def run_tests():
    with patch.dict(probe.os.environ, {"GEMINI_API_KEY": "offline-test-key"}):
        with patch.object(probe, "_call_model", return_value=(True, 200, "WARASHIBE_GEMINI_OK")) as call:
            result = probe.run_live_probe()
            assert result["status"] == "success"
            assert result["fallback_used"] is False
            assert result["selected_model"] == probe.PRIMARY_MODEL
            assert call.call_count == 1

        with patch.object(probe, "_call_model", side_effect=[
            (False, 503, "http_503"),
            (True, 200, "WARASHIBE_GEMINI_OK"),
        ]) as call, patch.object(probe.time, "sleep") as sleep:
            result = probe.run_live_probe()
            assert result["status"] == "success"
            assert result["fallback_used"] is True
            assert result["selected_model"] == probe.FALLBACK_MODELS[0]
            assert call.call_count == 2
            sleep.assert_called_once_with(1)

        with patch.object(probe, "_call_model", return_value=(False, 400, "http_400")) as call:
            result = probe.run_live_probe()
            assert result["status"] == "failed"
            assert result["fallback_used"] is False
            assert call.call_count == 1

        with patch.object(probe, "_call_model", return_value=(False, 503, "http_503")) as call, patch.object(probe.time, "sleep"):
            result = probe.run_live_probe()
            assert result["status"] == "failed"
            assert result["selected_model"] is None
            assert call.call_count == 1 + len(probe.FALLBACK_MODELS)

    with patch.dict(probe.os.environ, {}, clear=True), patch.object(probe, "_call_model") as call:
        result = probe.run_live_probe()
        assert result["status"] == "skipped"
        assert result["reason"] == "gemini_api_key_missing"
        call.assert_not_called()


if __name__ == "__main__":
    run_tests()
    print("Gemini offline fallback tests passed")
