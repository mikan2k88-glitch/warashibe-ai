"""v8.0 research release endpoint: separated implementation and acceptance gates."""
from flask import Blueprint, jsonify, render_template_string
from .v79_shadow_status import latest_shadow

v80_bp=Blueprint("dropship_v80",__name__,url_prefix="/dropship/v8.0")
REQUIRED={
    "ebay_seller_category_fees":"unverified",
    "cj_return_loss_model":"unverified",
    "verified_refund_reserve":"unverified",
    "sale_price_evidence":"unverified",
    "fx_and_settlement_cost":"unverified",
    "multi_day_shadow_validation":"incomplete",
}

def acceptance(shadow=None):
    shadow=shadow if shadow is not None else latest_shadow()
    reasons=[name for name,state in REQUIRED.items() if state!="verified"]
    if shadow.get("status")!="observed" or shadow.get("run_conclusion")!="success":
        reasons.append("recent_shadow_workflow_success")
    return {"version":"8.0","release":"research_mvp",
            "research_platform":"implemented",
            "shadow":shadow,
            "acceptance":"blocked_pending_verified_evidence",
            "required_evidence":dict(REQUIRED),
            "blocking_reasons":reasons,
            "human_gate_required":True,"human_gate_ready":False,
            "automatic_listing":False,"automatic_ordering":False,
            "live_execution_allowed":False}

@v80_bp.get("/endpoint")
def endpoint():
    return jsonify(acceptance())

@v80_bp.get("/dashboard")
def dashboard():
    result=acceptance()
    return render_template_string("""<!doctype html><html lang="ja"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Warashibe v8.0 研究運用</title>
<style>body{font-family:system-ui,sans-serif;max-width:800px;margin:30px auto;padding:16px}
section{border:1px solid #ccc;border-radius:12px;padding:15px;margin:15px 0}li{padding:5px}
a{color:#1258a1}strong{color:#a32a20}</style></head><body>
<h1>ドロップシッピングわらしべ v8.0</h1>
<p>研究運用版。実出品・発注・決済はすべて無効です。</p>
<section><h2>研究運用状況</h2>
<p>研究プラットフォーム：実装済み</p>
<p>最新Shadow：{{ shadow.status | e }} / {{ shadow.run_conclusion or 'unknown' | e }}</p>
<p>Human Gate：<strong>閉鎖</strong></p>
{% if shadow.run_url %}<a href="{{shadow.run_url|e}}">最新のShadow実行履歴</a>{% endif %}
</section><section><h2>実運用審査に必要な証拠</h2><ul>
{% for name,state in evidence.items() %}<li>{{name|e}}：<strong>{{state|e}}</strong></li>{% endfor %}
</ul></section><section><h2>関連API</h2>
<p><a href="/dropship/v8.0/endpoint">v8.0 審査ステータスJSON</a></p>
<p><a href="/dropship/v7.4/endpoint">採算・資金の評価</a></p>
<p><a href="/dropship/v7.7/endpoint">Shadow監査</a></p>
</section></body></html>""",shadow=result["shadow"],evidence=result["required_evidence"])
