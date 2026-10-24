import json
from types import SimpleNamespace
from scripts import dropship_actual_evidence as module

def test_evidence_reuses_resolved_cj_token(monkeypatch,capsys):
    provider=SimpleNamespace(token="existing-token")
    monkeypatch.setattr(module,"build_real_runtime_sources",lambda:{"status":"ready","supplier_provider":provider,"market_provider":object()})
    monkeypatch.setattr(module,"assess_persistence_environment",lambda:{"status":"ready"})
    observed=[]
    def fake_handshake(*,cj_token_provider):
        observed.append(cj_token_provider.get_token())
        return {"status":"real_provider_handshake_ready"}
    monkeypatch.setattr(module,"run_provider_handshake",fake_handshake)
    monkeypatch.setattr(module,"SupabaseRestClient",lambda:object())
    monkeypatch.setattr(module,"CJFreightEvidenceProvider",lambda **kw: object())
    monkeypatch.setattr(module,"run_actual_evidence_controller_v67",lambda *args,**kwargs:{"live_execution_allowed":False})
    module.main()
    assert observed==["existing-token"]
    assert json.loads(capsys.readouterr().out)["live_execution_allowed"] is False
