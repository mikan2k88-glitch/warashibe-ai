"""Warashibe CEO Dashboard.

Human-readable HQ status page plus a JSON surface that ChatGPT or other clients
can consume. The dashboard is read-only and never authorizes commerce.
"""

from flask import Blueprint, jsonify

from research_lab.hq_development_program import build_hq_development_program

hq_dashboard_bp = Blueprint("hq_dashboard", __name__)

_DEVELOPMENT_SUMMARY = [
    {
        "priority": "P1",
        "title": "HQ Runner Integration",
        "development_status": "complete",
        "operational_status": "complete",
        "summary": "定時開発をHQのPriority Queue経由で選択する制御へ接続。",
    },
    {
        "priority": "P2",
        "title": "Real Pilot Readiness",
        "development_status": "complete",
        "operational_status": "active",
        "summary": "実商品1件の判断パケットを作る段階。現在の最優先。",
    },
    {
        "priority": "P3",
        "title": "CEO Approval Gate",
        "development_status": "complete",
        "operational_status": "waiting",
        "summary": "候補商品をCEOに提示し、実購入前にHuman Gateで停止。",
    },
    {
        "priority": "P4",
        "title": "One Item Live Proof",
        "development_status": "complete",
        "operational_status": "waiting_human_gate",
        "summary": "購入・受領・販売・精算の1サイクルを証拠付きで実証。",
    },
    {
        "priority": "P5",
        "title": "Learning Feedback",
        "development_status": "complete",
        "operational_status": "waiting",
        "summary": "実績を次の商品評価へ戻すLearning Loop。",
    },
    {
        "priority": "P6",
        "title": "Capital Velocity Improvement",
        "development_status": "complete",
        "operational_status": "waiting",
        "summary": "利益だけでなく資金回転日数を含めて候補を順位付け。",
    },
    {
        "priority": "P7",
        "title": "Controlled Automation Expansion",
        "development_status": "complete",
        "operational_status": "waiting_live_evidence",
        "summary": "実証済みの安全な範囲だけ自動化対象を広げる。",
    },
]


def build_hq_dashboard_payload(candidate=None):
    candidate_payload = candidate or {
        "state": "live_screened_hold",
        "headline": "P2候補を実市場でスクリーニング済み",
        "message": (
            "Nintendo Switch『ウルトラ怪獣モンスターファーム』を実市場で確認。"
            "売買実績は確認できるものの、通販仕入れでは手数料・送料込みで赤字になるため、"
            "現時点ではP3へ上げない判断です。"
        ),
        "item_name": "ウルトラ怪獣モンスターファーム",
        "source": "駿河屋MEGA中筋店",
        "source_url": (
            "https://www.suruga-ya.jp/product/detail/"
            "109002348?tenpo_cd=400479&branch_number=0001"
        ),
        "sale_comp_source": "メルカリ売却済み実績",
        "sale_comp_url": "https://jp.mercari.com/item/m10992476959",
        "purchase_price_jpy": 1940,
        "source_shipping_min_jpy": 600,
        "expected_sale_price_jpy": 2500,
        "selling_fee_jpy": 250,
        "outbound_shipping_jpy": 210,
        "expected_net_profit_jpy": -500,
        "expected_margin_rate": -0.20,
        "estimated_days_to_sell": None,
        "capital_velocity_jpy_per_day": None,
        "max_loss_jpy": 500,
        "stop_loss_price_jpy": None,
        "risk": "economics_blocked",
        "go_to_p3": False,
        "screened_at": "2026-10-03",
        "economics": {
            "sale_net_after_fee_and_shipping_jpy": 2040,
            "local_pickup_profit_jpy": 100,
            "remote_purchase_profit_jpy": -500,
            "remote_purchase_total_cost_jpy": 2540,
        },
        "decision": "P3へ上げない",
        "next_search_gate": {
            "target_total_acquisition_cost_jpy_max": 2200,
            "target_net_profit_jpy_min": 300,
            "target_condition": (
                "3,000円資本内で、販売手数料と発送費を差し引いても"
                "最低300円以上の利益余地が残る候補"
            ),
        },
    }

    program = build_hq_development_program(
        operational_evidence={
            "hq_runner_integrated": True,
            "real_pilot_decision_packet_ready": False,
            "ceo_approval_gate_ready": False,
            "live_pilot_verified": False,
            "learning_feedback_ingested": False,
            "capital_velocity_optimized": False,
            "controlled_automation_scope_ready": False,
        }
    )

    return {
        "status": "hq_dashboard_ready",
        "title": "Warashibe CEO Dashboard",
        "north_star": "約3,000円 → 常に1商品 → 100万円",
        "current_phase": "P2",
        "development_endpoint": "P7",
        "current_bottleneck": "real_external_single_item_pilot_not_verified",
        "active_strategy": [
            "real_pilot_readiness",
            "ceo_approval_gate",
            "one_item_live_proof",
            "learning_feedback",
            "capital_velocity_improvement",
            "controlled_automation_expansion",
        ],
        "candidate": candidate_payload,
        "development_summary": list(_DEVELOPMENT_SUMMARY),
        "hq_program": program,
        "human_gate": {
            "required_for_real_commerce": True,
            "actions": [
                "real_purchase",
                "real_payment",
                "real_listing",
                "real_sale",
                "real_money_movement",
            ],
        },
        "dashboard_mode": "read_only",
        "external_execution_authorized": False,
    }


def _money(value):
    if value is None:
        return "—"
    return f"¥{int(round(value)):,}"


def _percent(value):
    if value is None:
        return "—"
    return f"{float(value) * 100:.1f}%"


def _metric(value, suffix=""):
    if value is None:
        return "—"
    return f"{value}{suffix}"


@hq_dashboard_bp.get("/hq/api")
def hq_dashboard_api():
    return jsonify(build_hq_dashboard_payload())


@hq_dashboard_bp.get("/hq")
def hq_dashboard_page():
    data = build_hq_dashboard_payload()
    candidate = data["candidate"]

    rows = "".join(
        f"""
        <div class="roadmap-row">
          <div class="badge">{row['priority']}</div>
          <div class="roadmap-copy">
            <strong>{row['title']}</strong>
            <span>{row['summary']}</span>
          </div>
          <div class="state {row['operational_status']}">{row['operational_status']}</div>
        </div>
        """
        for row in data["development_summary"]
    )

    return f"""
    <!doctype html>
    <html lang="ja">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Warashibe CEO Dashboard</title>
      <style>
        :root {{
          color-scheme: dark;
          --bg:#0b1020; --panel:#121a2d; --panel2:#182238; --line:#2b3857;
          --text:#f3f7ff; --muted:#9fb0cc; --accent:#73a7ff; --good:#73d6a3;
          --warn:#f5c96b; --danger:#ff8c8c;
        }}
        * {{ box-sizing:border-box; }}
        body {{ margin:0; background:linear-gradient(180deg,#080d19,#0d1424);
          color:var(--text); font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
        .wrap {{ max-width:1180px; margin:0 auto; padding:30px 20px 60px; }}
        .top {{ display:flex; gap:16px; align-items:flex-start; justify-content:space-between; flex-wrap:wrap; }}
        h1 {{ margin:0 0 6px; font-size:30px; }}
        .sub {{ color:var(--muted); }}
        .phase {{ background:#1c2b4b; border:1px solid #355587; border-radius:999px; padding:10px 16px; font-weight:800; }}
        .grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin:24px 0; }}
        .card {{ background:rgba(18,26,45,.92); border:1px solid var(--line); border-radius:18px; padding:18px; box-shadow:0 18px 50px rgba(0,0,0,.18); }}
        .label {{ color:var(--muted); font-size:13px; margin-bottom:8px; }}
        .value {{ font-size:24px; font-weight:800; }}
        .section-title {{ font-size:18px; margin:28px 0 12px; }}
        .candidate {{ display:grid; grid-template-columns:1.3fr 1fr; gap:16px; }}
        .candidate h2 {{ margin-top:0; }}
        .muted {{ color:var(--muted); }}
        .metrics {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
        .metric {{ background:var(--panel2); border-radius:12px; padding:12px; }}
        .roadmap-row {{ display:grid; grid-template-columns:52px 1fr auto; gap:12px; align-items:center; padding:13px 0; border-top:1px solid var(--line); }}
        .roadmap-row:first-child {{ border-top:0; }}
        .badge {{ width:42px; height:42px; border-radius:12px; background:#22304e; display:flex; align-items:center; justify-content:center; font-weight:800; }}
        .roadmap-copy {{ display:flex; flex-direction:column; gap:4px; }}
        .roadmap-copy span {{ color:var(--muted); font-size:13px; }}
        .state {{ border-radius:999px; padding:7px 10px; font-size:12px; border:1px solid var(--line); color:var(--muted); }}
        .active {{ color:var(--good); border-color:#2f7557; }}
        .complete {{ color:var(--good); }}
        .waiting_human_gate {{ color:var(--warn); border-color:#80692f; }}
        .human {{ border-left:4px solid var(--warn); }}
        .footer {{ color:var(--muted); margin-top:22px; font-size:13px; }}
        code {{ color:#bad2ff; }}
        @media (max-width:850px) {{
          .grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
          .candidate {{ grid-template-columns:1fr; }}
        }}
        @media (max-width:560px) {{
          .grid {{ grid-template-columns:1fr; }}
          .roadmap-row {{ grid-template-columns:46px 1fr; }}
          .state {{ grid-column:2; justify-self:start; }}
        }}
      </style>
    </head>
    <body>
      <main class="wrap">
        <div class="top">
          <div>
            <h1>Warashibe CEO Dashboard</h1>
            <div class="sub">North Star: {data['north_star']}</div>
          </div>
          <div class="phase">現在フェーズ: {data['current_phase']}</div>
        </div>

        <div class="grid">
          <div class="card"><div class="label">開発エンドポイント</div><div class="value">{data['development_endpoint']}</div></div>
          <div class="card"><div class="label">実運用の現在地</div><div class="value">{data['current_phase']}</div></div>
          <div class="card"><div class="label">Human Gate</div><div class="value">有効</div></div>
          <div class="card"><div class="label">取引自動実行</div><div class="value">OFF</div></div>
        </div>

        <div class="section-title">実商品候補</div>
        <section class="candidate">
          <div class="card">
            <h2>{candidate['headline']}</h2>
            <p class="muted">{candidate['message']}</p>
            <p><strong>候補:</strong> {candidate['item_name']}</p>
            <p><strong>判定:</strong> {candidate['decision']}</p>
            <p><strong>理由:</strong> 通販仕入れ総額 {_money(candidate['economics']['remote_purchase_total_cost_jpy'])} に対し、売却後の手取り想定は {_money(candidate['economics']['sale_net_after_fee_and_shipping_jpy'])}。現状は採算ゲート未達です。</p>
            <p><strong>次の探索条件:</strong> 総仕入コスト {_money(candidate['next_search_gate']['target_total_acquisition_cost_jpy_max'])} 以下、純利益 {_money(candidate['next_search_gate']['target_net_profit_jpy_min'])} 以上。</p>
            <p><strong>現在のボトルネック:</strong><br><code>{data['current_bottleneck']}</code></p>
          </div>
          <div class="card">
            <div class="metrics">
              <div class="metric"><div class="label">仕入本体</div><strong>{_money(candidate['purchase_price_jpy'])}</strong></div>
              <div class="metric"><div class="label">想定売価</div><strong>{_money(candidate['expected_sale_price_jpy'])}</strong></div>
              <div class="metric"><div class="label">通販時想定利益</div><strong>{_money(candidate['expected_net_profit_jpy'])}</strong></div>
              <div class="metric"><div class="label">利益率</div><strong>{_percent(candidate['expected_margin_rate'])}</strong></div>
              <div class="metric"><div class="label">売却日数</div><strong>{_metric(candidate['estimated_days_to_sell'],'日')}</strong></div>
              <div class="metric"><div class="label">Capital Velocity</div><strong>{_money(candidate['capital_velocity_jpy_per_day'])}/日</strong></div>
            </div>
          </div>
        </section>

        <div class="section-title">開発サマリー</div>
        <section class="card">{rows}</section>

        <div class="section-title">CEO / Human Gate</div>
        <section class="card human">
          <strong>実購入・実決済・実出品・実販売・実資金移動はCEO判断が必要です。</strong>
          <p class="muted">このDashboardは表示・判断支援専用で、取引を自動実行しません。</p>
        </section>

        <div class="footer">
          JSON: <code>/hq/api</code> — ChatGPTや他の表示UIから同じHQ状態を取得できます。
        </div>
      </main>
    </body>
    </html>
    """


__all__ = ["hq_dashboard_bp", "build_hq_dashboard_payload"]
