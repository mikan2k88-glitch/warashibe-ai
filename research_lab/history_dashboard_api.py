"""PG-019 read-only Human Review / price / plan / economics history dashboard.

The dashboard is observational only. It never mutates review, plan, economics, or
commerce state and never authorizes an external action.
"""

import hmac
import os

from flask import Blueprint, jsonify, render_template_string, request

API_VERSION = "0.1"


class SupabaseHistoryReader:
    def __init__(self, client):
        if client is None:
            raise ValueError("client is required")
        self.client = client

    def records(self, identity_key, limit=20):
        response = (
            self.client.table("warashibe_cross_market_records")
            .select("record_key,identity_key,comparison,proposal,observed_at,captured_at")
            .eq("identity_key", identity_key)
            .order("captured_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [dict(row) for row in (response.data or [])]

    def reviews(self, identity_key, limit=20):
        response = (
            self.client.table("warashibe_review_decisions")
            .select("record_key,identity_key,decision,reviewer_id,reason,reviewed_at")
            .eq("identity_key", identity_key)
            .order("reviewed_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [dict(row) for row in (response.data or [])]

    def plans(self, identity_key, limit=20):
        response = (
            self.client.table("warashibe_dry_run_plans")
            .select("plan_key,source_record_key,identity_key,review_decision,plan,generated_at")
            .eq("identity_key", identity_key)
            .order("generated_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [dict(row) for row in (response.data or [])]

    def economics(self, identity_key, limit=20):
        response = (
            self.client.table("warashibe_economic_assessments")
            .select("assessment_key,plan_key,identity_key,economics,evaluated_at")
            .eq("identity_key", identity_key)
            .order("evaluated_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [dict(row) for row in (response.data or [])]


def _runtime_dependencies():
    review_code = str(os.environ.get("WARASHIBE_REVIEW_CODE") or "").strip()
    url = str(os.environ.get("SUPABASE_URL") or "").strip()
    key = str(
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
        or ""
    ).strip()
    if not review_code or not url or not key:
        return None
    from supabase import create_client
    return SupabaseHistoryReader(create_client(url, key)), review_code


def _call_history(repo, identity_key, limit):
    if hasattr(repo, "history_for_identity"):
        return repo.history_for_identity(identity_key, limit=limit)
    if hasattr(repo, "list_for_identity"):
        return repo.list_for_identity(identity_key, limit=limit)
    raise RuntimeError("history repository does not support identity history")


def _snapshot(records, reviews, plans, economics):
    latest_record = records[0] if records else {}
    latest_review = reviews[0] if reviews else {}
    latest_plan = plans[0] if plans else {}
    latest_economics = economics[0] if economics else {}
    comparison = latest_record.get("comparison") or {}
    econ = latest_economics.get("economics") or {}
    return {
        "record_key": latest_record.get("record_key"),
        "lowest_asking_price_jpy": comparison.get("lowest_asking_price_jpy"),
        "highest_asking_price_jpy": comparison.get("highest_asking_price_jpy"),
        "review_decision": latest_review.get("decision"),
        "plan_key": latest_plan.get("plan_key"),
        "assessment_key": latest_economics.get("assessment_key"),
        "expected_net_profit_jpy": econ.get("expected_net_profit_jpy"),
        "break_even_price_jpy": econ.get("break_even_price_jpy"),
        "stop_loss_price_jpy": econ.get("stop_loss_price_jpy"),
        "economically_viable": (econ.get("profit_gate") or {}).get("economically_viable"),
    }


def create_history_dashboard_blueprint(
    *,
    record_repository=None,
    review_repository=None,
    plan_repository=None,
    economics_repository=None,
    review_code_provider=None,
):
    bp = Blueprint("history_dashboard", __name__)

    def resolve():
        injected = (
            record_repository,
            review_repository,
            plan_repository,
            economics_repository,
        )
        if all(repo is not None for repo in injected) and review_code_provider is not None:
            code = str(review_code_provider() or "").strip()
            if not code:
                return None
            return injected, code
        try:
            runtime = _runtime_dependencies()
        except Exception:
            return None
        if runtime is None:
            return None
        reader, code = runtime
        return ((reader, reader, reader, reader), code)

    @bp.get("/history")
    def history_page():
        return render_template_string(
            """<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Warashibe AI History Dashboard</title>
<style>
body{max-width:900px;margin:32px auto;padding:20px;font-family:sans-serif;line-height:1.6}
input,button{width:100%;box-sizing:border-box;padding:10px;margin:6px 0 14px}
pre{white-space:pre-wrap;word-break:break-word;background:#111;color:#eee;padding:14px;border-radius:8px}
.note{border-left:5px solid #555;padding-left:12px}
</style></head><body>
<h1>Warashibe AI History Dashboard</h1>
<p class="note">閲覧専用です。ここから購入・決済・販売は実行されません。</p>
<label>Identity Key</label><input id="identityKey">
<label>Review Code</label><input id="reviewCode" type="password">
<button onclick="loadHistory()">履歴を表示</button>
<pre id="view">未読込</pre>
<script>
async function loadHistory(){
 const res=await fetch("/api/history",{method:"POST",headers:{"Content-Type":"application/json"},
 body:JSON.stringify({identity_key:document.getElementById("identityKey").value,
 review_code:document.getElementById("reviewCode").value})});
 const data=await res.json();
 document.getElementById("view").textContent="HTTP "+res.status+"\n"+JSON.stringify(data,null,2);
}
</script></body></html>"""
        )

    @bp.post("/api/history")
    def history_api():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"status":"invalid_request","commerce_authorized":False}), 400

        resolved = resolve()
        if resolved is None:
            return jsonify({
                "status":"history_unavailable",
                "reason":"history_runtime_not_configured",
                "commerce_authorized":False,
                "external_action_authorized":False,
            }), 503

        repos, configured_code = resolved
        supplied = str(payload.get("review_code") or "")
        if not supplied or not hmac.compare_digest(supplied, configured_code):
            return jsonify({"status":"forbidden","commerce_authorized":False}), 403

        identity_key = str(payload.get("identity_key") or "").strip()
        if not identity_key:
            return jsonify({"status":"invalid_request","reason":"identity_key_required","commerce_authorized":False}), 400

        try:
            if isinstance(repos[0], SupabaseHistoryReader):
                records = repos[0].records(identity_key)
                reviews = repos[1].reviews(identity_key)
                plans = repos[2].plans(identity_key)
                economics = repos[3].economics(identity_key)
            else:
                records = _call_history(repos[0], identity_key, 20)
                reviews = _call_history(repos[1], identity_key, 20)
                plans = _call_history(repos[2], identity_key, 20)
                economics = _call_history(repos[3], identity_key, 20)
        except Exception:
            return jsonify({
                "status":"history_unavailable",
                "reason":"history_lookup_failed",
                "commerce_authorized":False,
            }), 503

        return jsonify({
            "version":API_VERSION,
            "status":"history_ready",
            "identity_key":identity_key,
            "latest_snapshot":_snapshot(records,reviews,plans,economics),
            "records":records,
            "reviews":reviews,
            "plans":plans,
            "economic_assessments":economics,
            "read_only":True,
            "execution_triggered":False,
            "commerce_authorized":False,
            "external_action_authorized":False,
        })

    return bp


history_dashboard_bp = create_history_dashboard_blueprint()
