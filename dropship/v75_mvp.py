"""v7.5 research MVP: usable public dashboard and truthful acceptance state.

All live provider reads run only in the scheduled, credentialed Actions workflow.
This public endpoint never invokes provider APIs, orders or marketplace writes.
"""
from flask import Blueprint, jsonify, render_template_string

v75_bp=Blueprint("dropship_v75",__name__,url_prefix="/dropship/v7.5")

STATUS={
    "version":"7.5",
    "release":"research_mvp",
    "research_pipeline":"deployed",
    "provider_shadow_workflow":"configured",
    "live_account_cost_evidence":"incomplete",
    "return_loss_evidence":"incomplete",
    "capital_and_fx_model":"available_requires_verified_inputs",
    "profit_proof":"not_established",
    "operational_acceptance":"pending",
    "next_actions":[
        "verify_ebay_seller_category_specific_fees",
        "verify_cj_return_losses_and_refund_reserve",
        "verify_fx_and_cash_flow_before_commerce",
        "accumulate_multi_day_shadow_evidence"
    ],
    "human_gate_required":True,"human_gate_ready":False,
    "automatic_listing":False,"automatic_ordering":False,
    "live_execution_allowed":False,
}

@v75_bp.get("/endpoint")
def endpoint():
    return jsonify(STATUS)

@v75_bp.get("/dashboard")
def dashboard():
    return render_template_string("""<!doctype html><html lang="ja">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>わらしべ ドロップシッピング 研究運用版</title>
<style>body{font-family:system-ui,sans-serif;max-width:820px;margin:35px auto;padding:0 18px;color:#182334}
h1{font-size:1.65em}section{border:1px solid #d5dbe4;border-radius:14px;padding:18px;margin:17px 0}
li{margin:9px 0}strong{color:#ba3d21}a{color:#1758a8}</style></head>
<body><h1>ドロップシッピングわらしべ v7.5</h1>
<p>研究運用版のシステム画面です。実売買は無効です。</p>
<section><h2>研究エンジン</h2><p>稼働基盤：実装・デプロイ済み</p>
<p>eBay手数料・返品損失・資金検証：<strong>未完了</strong></p>
<p>Human Gate：<strong>閉鎖</strong></p></section>
<section><h2>研究結果の確認</h2><ul>
<li><a href="/dropship/v7.5/endpoint">現在の受入ステータス（JSON）</a></li>
<li><a href="/dropship/v7.9/status">最新のShadow稼働状況（自動取得）</a></li>
<li><a href="/dropship/v7.4/endpoint">採算・資金評価API</a></li>
<li><a href="https://github.com/mikan2k88-glitch/warashibe-ai/actions/workflows/dropshipping-v70-shadow.yml">日次Shadow研究の履歴・証拠</a></li>
</ul></section>
<section><h2>実運用開始までの残作業</h2><ol>
<li>eBayの販売者・カテゴリ別手数料を確定</li>
<li>CJの返品・返金損失と準備金の根拠を確定</li>
<li>実際の為替・資金拘束を検証</li>
<li>Shadow観測を蓄積し、安全審査を受ける</li></ol>
</section><p>出品・注文・決済を実行する操作はありません。</p></body></html>""")
