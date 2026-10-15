import io
import json
from zipfile import ZipFile
from scripts import dropship_v78_collect as collector

def test_collect_sanitized_history(monkeypatch):
    stream=io.BytesIO()
    with ZipFile(stream,"w") as z:
        z.writestr("v70-shadow-observation.json",json.dumps({
            "status":"observation_captured","observed_at":"2026-10-15T09:00:00Z",
            "missing_evidence":["platform_fee"],"candidate_count":5}))
        z.writestr("v78-shadow-audit.json","{}")
    def fake_get(url, token, binary=False):
        if url.endswith("/zip"): return stream.getvalue()
        if "/workflows/" in url: return {"workflow_runs":[{"id":123,"conclusion":"success"}]}
        return {"artifacts":[{"id":456,"name":"v70-shadow-observation","expired":False,"size_in_bytes":500}]}
    monkeypatch.setattr(collector,"_get",fake_get)
    result=collector.collect("example/repo","safe-test-token")
    assert result["total_observations"]==1
    assert result["missing_evidence_counts"]["platform_fee"]==1
    assert result["human_gate_ready"] is False

def test_requires_token():
    import pytest
    with pytest.raises(ValueError):
        collector.collect("example/repo","")
