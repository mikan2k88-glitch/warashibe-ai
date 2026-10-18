import json
from urllib.error import HTTPError
from scripts import dropship_auto_debug as debug

def test_unauthorized_log_fails_closed(monkeypatch):
    def fake(url,token):
        if "/jobs?" in url:
            return json.dumps({"jobs":[{"id":17,"conclusion":"failure"}]})
        raise RuntimeError("github_http_401")
    monkeypatch.setattr(debug,"fetch",fake)
    result=debug.analyze_run("mikan2k88-glitch/warashibe-ai",123,"token")
    assert result["status"]=="diagnosed"
    assert result["findings"][0]["category"]=="logs_unavailable"
    assert result["findings"][0]["safe_to_retry"] is False
    assert result["live_execution_allowed"] is False

def test_failed_job_list_is_unavailable_not_success(monkeypatch,tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("REPO","owner/repo")
    monkeypatch.setenv("RUN_ID","123")
    monkeypatch.setenv("GH_TOKEN","token")
    def broken(*args):
        raise RuntimeError("github_http_401")
    monkeypatch.setattr(debug,"analyze_run",broken)
    debug.main()
    result=json.loads((tmp_path/"dropship-debug-diagnosis.json").read_text())
    assert result["status"]=="diagnosis_unavailable"
    assert result["live_execution_allowed"] is False
