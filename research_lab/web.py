"""Read-only Flask dashboard for Warashibe AI Research Lab."""

import json
import os
from pathlib import Path

from flask import Blueprint, jsonify, render_template_string

from research_lab import LAB_VERSION
from research_lab.config import LAB_BRANCH, PRODUCTION_BRANCH, RESEARCH_TRACKS
from research_lab.dashboard_kpis import research_kpis, route_probability_series
from research_lab.dashboard_uncertainty import demo_uncertainty_metrics
from research_lab.storage import ResearchRepository
from research_lab.github_actions_bridge import live_snapshot, workflow_runs
from research_lab.live_outcome_store import OutcomeStore

lab_bp = Blueprint("research_lab", __name__)
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(os.environ.get("WARASHIBE_LAB_OUTPUT", ROOT / "research_output"))

TEMPLATE = """<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="30"><title>Warashibe AI Lab</title>
<style>
:root{color-scheme:dark}body{font-family:system-ui,sans-serif;background:#080d18;color:#e8edf7;margin:0}.wrap{max-width:1180px;margin:auto;padding:28px}
h1{margin:0 0 4px}.muted{color:#91a0b8}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:22px 0}
.card{background:#121b2d;border:1px solid #263550;border-radius:16px;padding:18px;box-shadow:0 8px 30px #0003}.big{font-size:27px;font-weight:750}.ok{color:#6ee7a8}.bad{color:#ff7b86}.warn{color:#ffd166}
.flow{display:flex;align-items:center;gap:10px;overflow:auto;padding:12px 0}.node{min-width:170px;background:#18243a;border:1px solid #304363;border-radius:12px;padding:14px}.arrow{font-size:24px;color:#607493}
.bar{height:10px;background:#263550;border-radius:8px;overflow:hidden;margin-top:8px}.fill{height:100%;background:linear-gradient(90deg,#6ee7a8,#79a8ff)}
.chart{display:flex;align-items:flex-end;gap:5px;height:130px;padding:14px 4px 4px}.col{flex:1;min-width:5px;background:linear-gradient(#79a8ff,#6ee7a8);border-radius:4px 4px 0 0;opacity:.9}.chartlabel{display:flex;justify-content:space-between;color:#91a0b8;font-size:12px}
.probchart{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;height:220px;padding-top:12px}.probchart>div{height:190px;display:flex;flex-direction:column}.probgroup{height:165px;display:flex;align-items:flex-end;justify-content:center;gap:5px;border-bottom:1px solid #304363}.pbar{width:28%;min-width:12px;border-radius:5px 5px 0 0}.current{background:#607493}.optimal{background:#6ee7a8}.plabel{text-align:center;color:#91a0b8;font-size:12px;margin-top:7px}.legend{display:flex;gap:18px;font-size:12px;color:#91a0b8;margin-top:12px}
table{width:100%;border-collapse:collapse;background:#121b2d;border-radius:14px;overflow:hidden}th,td{padding:12px;text-align:left;border-bottom:1px solid #263550}th{color:#91a0b8}
code{color:#b7c7ff}@media(max-width:700px){.wrap{padding:16px}th:nth-child(3),td:nth-child(3){display:none}}
</style></head><body><div class="wrap">
<h1>Warashibe AI Research Lab</h1><div class="muted">研究所ライブモニター v{{ version }} · 30秒ごとに自動更新</div>
<div class="grid">
<div class="card"><div class="muted">LAB STATUS</div><div class="big {{ 'ok' if snapshot.status == 'passed' else 'bad' }}">{{ snapshot.status|upper }}</div></div>
<div class="card"><div class="muted">CURRENT STAGE</div><div class="big">{{ snapshot.stage }}</div></div>
<div class="card"><div class="muted">NEXT THEME</div><div class="big">{{ snapshot.next_theme }}</div></div>
<div class="card"><div class="muted">CHECKS</div><div class="big">{{ snapshot.passed_checks }}/{{ snapshot.total_checks }}</div><div class="bar"><div class="fill" style="width:{{ snapshot.check_percent }}%"></div></div></div>
</div>
<div class="card"><div class="muted">研究フロー</div><div class="flow"><div class="node">Evidence</div><div class="arrow">→</div><div class="node">Raw outcomes</div><div class="arrow">→</div><div class="node">Bayesian posterior</div><div class="arrow">→</div><div class="node">Route uncertainty</div><div class="arrow">→</div><div class="node">Ranking</div></div></div>
<div class="grid"><div class="card"><div class="muted">安定版</div><div class="big">{{ production }}</div></div><div class="card"><div class="muted">研究版</div><div class="big">{{ branch }}</div></div><div class="card"><div class="muted">記録済み実験</div><div class="big">{{ stats.total }}</div></div><div class="card"><div class="muted">最終更新</div><div>{{ snapshot.generated_at }}</div></div></div>
<h2>研究KPI</h2><div class="grid">
<div class="card"><div class="muted">BASELINE GOAL</div><div class="big">{{ "%.4f"|format(kpis.baseline_goal_probability_percent) }}%</div></div>
<div class="card"><div class="muted">BEST GOAL</div><div class="big ok">{{ "%.2f"|format(kpis.best_goal_probability_percent) }}%</div></div>
<div class="card"><div class="muted">RECOVERY</div><div class="big">{{ "%.0f"|format(kpis.best_recovery_rate_percent) }}%</div></div>
<div class="card"><div class="muted">TX | GOAL</div><div class="big">{{ "%.1f"|format(kpis.best_conditional_transactions) }}</div></div></div>
<h2>Goal到達確率</h2><div class="card">
<div class="muted">Recovery率別 · Current policy / Optimal policy</div>
<div class="probchart">{% for p in probabilities %}<div><div class="probgroup"><div class="pbar current" title="Current {{ '%.2f'|format(p.current_goal_probability_percent) }}%" style="height:{{ p.current_goal_probability_percent }}%"></div><div class="pbar optimal" title="Optimal {{ '%.2f'|format(p.optimal_goal_probability_percent) }}%" style="height:{{ p.optimal_goal_probability_percent }}%"></div></div><div class="plabel">{{ "%.0f"|format(p.recovery_rate_percent) }}%</div></div>{% endfor %}</div>
<div class="legend"><span>■ Current</span><span>■ Optimal</span><span>横軸: Recovery率</span></div></div>
<h2>不確実性モニター</h2><div class="card"><div class="muted">OUTCOME DATA MODE</div><div class="big">{{ outcome_stats.mode|upper }}</div><div class="muted">{{ outcome_stats.total }} outcomes · {{ outcome_stats.opportunities }} opportunities</div></div><div class="grid">
<div class="card"><div class="muted">PRIOR</div><div class="big">{{ "%.1f"|format(uncertainty.prior_probability_percent) }}%</div></div>
<div class="card"><div class="muted">POSTERIOR</div><div class="big">{{ "%.1f"|format(uncertainty.posterior_probability_percent) }}%</div></div>
<div class="card"><div class="muted">CONSERVATIVE</div><div class="big warn">{{ "%.1f"|format(uncertainty.conservative_probability_percent) }}%</div></div>
<div class="card"><div class="muted">UNCERTAINTY σ</div><div class="big">{{ "%.1f"|format(uncertainty.posterior_std_percent) }}pt</div></div>
<div class="card"><div class="muted">RAW OUTCOMES</div><div class="big">{{ uncertainty.raw_outcome_count }}</div></div>
<div class="card"><div class="muted">EVIDENCE / SOURCES</div><div class="big">{{ uncertainty.evidence_count }} / {{ uncertainty.source_count }}</div></div></div>
<div class="card muted">現在は研究用fixtureの可視化です。実市場outcomeが接続された段階で同じ計器をライブデータへ切り替えます。</div>
<h2>研究履歴</h2>
<div class="card"><div class="muted">CHECK PASS RATE · 直近{{ history|length }}サイクル</div>
{% if history %}<div class="chart">{% for h in history %}<div class="col" title="{{ h.generated_at }} · {{ h.check_percent }}%" style="height:{{ h.check_percent }}%"></div>{% endfor %}</div>
<div class="chartlabel"><span>過去</span><span>現在</span></div>{% else %}<p class="muted">次回研究サイクルから履歴を蓄積します。</p>{% endif %}</div>
<h2>最新研究</h2>
{% if experiments %}<table><tr><th>ID</th><th>研究</th><th>日時</th><th>判断</th></tr>{% for e in experiments %}<tr><td>{{ e.id }}</td><td>{{ e.title }}<br><span class="muted">{{ e.track }}</span></td><td>{{ e.created_at }}</td><td>{{ e.decision }}</td></tr>{% endfor %}</table>{% else %}<div class="card muted">研究DBは準備済みです。まだ永続化された実験結果はありません。</div>{% endif %}
<p class="muted">API: <code>/lab/api/status</code></p></div></body></html>"""


def _repo():
    return ResearchRepository()


def _history():
    runs = workflow_runs()
    if runs:
        rows = []
        for run in reversed(runs[-40:]):
            rows.append({"generated_at": run["updated_at"], "status": run["conclusion"] or run["status"], "check_percent": 100 if run["conclusion"] == "success" else 0})
        return rows
    path = OUTPUT / "history.json"
    if not path.exists():
        return []
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    for row in rows:
        total = row.get("total_checks", 0)
        row["check_percent"] = round(100 * row.get("passed_checks", 0) / total) if total else 0
    return rows[-40:]


def _snapshot():
    live = live_snapshot("dashboard_uncertainty_monitor", "live_outcome_dashboard_bridge", 17)
    if live:
        return live
    path = OUTPUT / "latest.json"
    data = {"status": "waiting", "stage": "bootstrap", "next_theme": "research_cycle", "generated_at": None, "checks": []}
    if path.exists():
        try:
            data.update(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            data["status"] = "snapshot_error"
    checks = data.get("checks") or []
    passed = sum(1 for check in checks if check.get("returncode") == 0)
    data["passed_checks"] = passed
    data["total_checks"] = len(checks)
    data["check_percent"] = round(100 * passed / len(checks)) if checks else 0
    return data


@lab_bp.route("/lab")
def dashboard():
    repository = _repo()
    return render_template_string(TEMPLATE, version=LAB_VERSION, production=PRODUCTION_BRANCH,
        branch=LAB_BRANCH, tracks=RESEARCH_TRACKS, stats=repository.stats(),
        experiments=repository.recent(20), snapshot=_snapshot(), history=_history(), kpis=research_kpis(), probabilities=route_probability_series(), uncertainty=demo_uncertainty_metrics(), outcome_stats=OutcomeStore().stats())


@lab_bp.route("/lab/api/status")
def status():
    repository = _repo()
    return jsonify({"lab_version": LAB_VERSION, "production_branch": PRODUCTION_BRANCH,
        "research_branch": LAB_BRANCH, "tracks": RESEARCH_TRACKS, "snapshot": _snapshot(),
        "stats": repository.stats(), "kpis": research_kpis(), "route_probabilities": route_probability_series(), "uncertainty": demo_uncertainty_metrics(), "outcome_store": OutcomeStore().stats(), "history": _history(), "recent_experiments": repository.recent(20)})
