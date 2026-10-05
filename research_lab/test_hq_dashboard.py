"""Dashboard uses saved observations and refuses invented activity claims."""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
from app import app
from research_lab.hq_dashboard import build_hq_dashboard_payload
from research_lab.shadow_repository import JsonShadowRepository, InMemoryShadowRepository
from research_lab.test_shadow_promotion import shadow_fixture, NOW, LATER

def main():
    payload = build_hq_dashboard_payload(shadow_repository=InMemoryShadowRepository(), as_of=NOW)
    assert payload['current_phase'] == 'P1'
    assert payload['candidate']['state'] == 'not_observed'
    assert payload['system_status']['hq_runner'] == 'not_verified'
    assert payload['strategy_learning']['status'] == 'not_verified'
    assert payload['human_gate_required'] is True
    assert payload['external_execution_authorized'] is False
    assert all(r['operational_status'] == 'not_verified' for r in payload['development_summary'])
    with tempfile.TemporaryDirectory() as directory:
        store = Path(directory) / 'shadow.json'
        repo, shadow = shadow_fixture(JsonShadowRepository(store))
        candidate = build_hq_dashboard_payload(shadow_repository=repo, as_of=NOW)['candidate']
        assert candidate['shadow_candidate_id'] == shadow['shadow_candidate_id']
        assert candidate['observed_at'] == NOW
        assert candidate['item_name'] == 'Fixture only'
        snapshot = Path(directory) / 'runner.json'
        evidence = {'generated_at': NOW, 'head_sha': 'a'*40, 'status': 'passed', 'profile': 'build',
                    'selected_priority': 'P2', 'human_gate_preserved': True,
                    'external_execution_authorized': False, 'checks': [{'returncode': 0}]}
        snapshot.write_text(json.dumps(evidence), encoding='utf-8')
        with patch.dict(os.environ, {'WARASHIBE_RUNNER_SNAPSHOT': str(snapshot), 'WARASHIBE_EXPECTED_HEAD_SHA': 'a'*40}):
            good = build_hq_dashboard_payload(shadow_repository=repo, as_of=NOW)
            assert good['system_status']['hq_runner'] == 'observed_success'
            assert good['current_phase'] == 'P2'
            assert good['strategy_learning']['status'] == 'not_verified'
            for change in ({'head_sha': 'b'*40}, {'generated_at': '2020-01-01T00:00:00Z'},
                           {'generated_at': LATER}, {'status': 'failed'}, {'checks': []},
                           {'external_execution_authorized': True}):
                snapshot.write_text(json.dumps({**evidence, **change}), encoding='utf-8')
                bad = build_hq_dashboard_payload(shadow_repository=repo, as_of=NOW)
                assert bad['system_status']['hq_runner'] == 'not_verified'
            snapshot.write_text('broken', encoding='utf-8')
            assert build_hq_dashboard_payload(shadow_repository=repo, as_of=NOW)['current_phase'] == 'P1'
        data = json.loads(store.read_text(encoding='utf-8'))
        data['candidates'][0]['product_name'] = '<script>alert(1)</script>'
        store.write_text(json.dumps(data), encoding='utf-8')
        with patch.dict(os.environ, {'WARASHIBE_SHADOW_STORE': str(store)}):
            client = app.test_client()
            assert client.get('/hq/api').get_json()['candidate']['item_name'] == '<script>alert(1)</script>'
            page = client.get('/hq')
            assert page.status_code == 200
            html = page.get_data(as_text=True)
            assert '<script>alert(1)</script>' not in html
            assert '&lt;script&gt;alert(1)&lt;/script&gt;' in html
            assert '稼働中:' not in html
            assert 'ウルトラ怪獣モンスターファーム' not in html
            assert '本番ルールは自動変更しません' in html
    print('Evidence-driven Dashboard tests passed')

if __name__ == '__main__':
    main()
