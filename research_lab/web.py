"""Read-only Flask dashboard for Warashibe AI Research Lab."""

from flask import Blueprint, jsonify, render_template_string

from research_lab import LAB_VERSION
from research_lab.config import LAB_BRANCH, PRODUCTION_BRANCH, RESEARCH_TRACKS
from research_lab.storage import ResearchRepository

lab_bp = Blueprint("research_lab", __name__)

TEMPLATE = """<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Warashibe AI Lab</title>
<style>
body{font-family:system-ui,sans-serif;background:#0b1020;color:#e8edf7;margin:0}.wrap{max-width:1100px;margin:auto;padding:28px}
h1{margin-bottom:4px}.muted{color:#9ba8bd}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:22px 0}
.card{background:#151d31;border:1px solid #27334e;border-radius:14px;padding:18px}.big{font-size:28px;font-weight:700}.ok{color:#73e2a7}
table{width:100%;border-collapse:collapse;background:#151d31;border-radius:14px;overflow:hidden}th,td{padding:12px;text-align:left;border-bottom:1px solid #27334e}th{color:#9ba8bd}
code{color:#b7c7ff}@media(max-width:700px){th:nth-child(3),td:nth-child(3){display:none}}
</style></head><body><div class="wrap">
<h1>Warashibe AI Research Lab</h1><div class="muted">研究所ダッシュボード v{{ version }}</div>
<div class="grid"><div class="card"><div class="muted">STATUS</div><div class="big ok">RUNNING</div></div>
<div class="card"><div class="muted">安定版</div><div class="big">{{ production }}</div></div>
<div class="card"><div class="muted">研究版</div><div class="big">{{ branch }}</div></div>
<div class="card"><div class="muted">記録済み実験</div><div class="big">{{ stats.total }}</div></div></div>
<div class="card"><div class="muted">研究トラック</div><p>{{ tracks|join(" → ") }}</p></div>
<h2>最新研究</h2>
{% if experiments %}<table><tr><th>ID</th><th>研究</th><th>日時</th><th>判断</th></tr>
{% for e in experiments %}<tr><td>{{ e.id }}</td><td>{{ e.title }}<br><span class="muted">{{ e.track }}</span></td><td>{{ e.created_at }}</td><td>{{ e.decision }}</td></tr>{% endfor %}</table>
{% else %}<div class="card muted">研究DBは準備済みです。まだ永続化された実験結果はありません。</div>{% endif %}
<p class="muted">JSON: <code>/lab/api/status</code></p></div></body></html>"""


def _repo():
    return ResearchRepository()


@lab_bp.route("/lab")
def dashboard():
    repository = _repo()
    return render_template_string(TEMPLATE, version=LAB_VERSION, production=PRODUCTION_BRANCH,
        branch=LAB_BRANCH, tracks=RESEARCH_TRACKS, stats=repository.stats(), experiments=repository.recent(20))


@lab_bp.route("/lab/api/status")
def status():
    repository = _repo()
    return jsonify({"lab_version": LAB_VERSION, "production_branch": PRODUCTION_BRANCH,
        "research_branch": LAB_BRANCH, "tracks": RESEARCH_TRACKS,
        "stats": repository.stats(), "recent_experiments": repository.recent(20)})
