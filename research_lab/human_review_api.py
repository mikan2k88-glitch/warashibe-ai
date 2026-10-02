"""Human Review API/UI for PG-016.

Review approval is an append-only audit event only. This module never invokes
the commerce execution gate and never authorizes purchase, payment, or sale.
"""

import hmac
import os
from datetime import datetime, timezone

from flask import Blueprint, jsonify, render_template_string, request

from research_lab.human_review_decision import (
    build_human_review_decision,
    evaluate_review_eligibility,
)
from research_lab.supabase_cross_market_record_repository import (
    SupabaseCrossMarketRecordRepository,
)
from research_lab.supabase_review_decision_repository import (
    SupabaseReviewDecisionRepository,
)

API_VERSION = "0.1"


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

    client = create_client(url, key)
    return (
        SupabaseCrossMarketRecordRepository(client),
        SupabaseReviewDecisionRepository(client),
        review_code,
    )


def create_human_review_blueprint(
    *,
    record_repository=None,
    review_repository=None,
    review_code_provider=None,
    now_provider=None,
):
    bp = Blueprint("human_review", __name__)
    now_provider = now_provider or (lambda: datetime.now(timezone.utc))

    def resolve():
        if (
            record_repository is not None
            and review_repository is not None
            and review_code_provider is not None
        ):
            code = str(review_code_provider() or "").strip()
            if not code:
                return None
            return record_repository, review_repository, code
        try:
            return _runtime_dependencies()
        except Exception:
            return None

    def authorize(payload, configured_code):
        supplied = str((payload or {}).get("review_code") or "")
        return bool(supplied) and hmac.compare_digest(supplied, configured_code)

    def unavailable():
        return jsonify({
            "status": "review_unavailable",
            "reason": "review_runtime_not_configured",
            "commerce_authorized": False,
            "external_action_authorized": False,
        }), 503

    @bp.get("/review")
    def review_page():
        return render_template_string(
            """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Warashibe AI Human Review</title>
<style>
body{max-width:760px;margin:32px auto;padding:20px;font-family:sans-serif;line-height:1.6}
section{padding:18px;margin:18px 0;background:#f5f5f5;border-radius:10px}
input,textarea,button{width:100%;box-sizing:border-box;padding:10px;margin:6px 0 14px}
button{cursor:pointer}.warning{border-left:5px solid #b71c1c;padding-left:12px}
.actions{display:grid;grid-template-columns:1fr 1fr;gap:12px}
pre{white-space:pre-wrap;word-break:break-word;background:#111;color:#eee;padding:12px;border-radius:8px}
</style>
</head>
<body>
<h1>Warashibe AI Human Review</h1>
<p class="warning">approve は購入命令ではありません。レビュー監査記録だけを作成します。</p>
<section>
<label>Identity Key</label>
<input id="identityKey" placeholder="gtin:...:JPY">
<label>Review Code</label>
<input id="reviewCode" type="password" autocomplete="one-time-code">
<button type="button" onclick="loadReview()">最新候補を読み込む</button>
</section>
<section>
<h2>レビュー対象</h2>
<pre id="recordView">未読込</pre>
<label>Reason</label>
<textarea id="reason" placeholder="判断理由を入力"></textarea>
<div class="actions">
<button type="button" onclick="submitDecision('approve')">approve</button>
<button type="button" onclick="submitDecision('reject')">reject</button>
</div>
</section>
<section>
<h2>結果</h2>
<pre id="resultView">未実行</pre>
</section>
<p>commerce authorization は常に false のままです。</p>
<script>
let loadedRecordKey = null;
async function postJson(path, body){
  const response = await fetch(path, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(body)
  });
  const data = await response.json();
  return {status: response.status, data};
}
async function loadReview(){
  loadedRecordKey = null;
  const result = await postJson("/api/review/latest", {
    identity_key: document.getElementById("identityKey").value,
    review_code: document.getElementById("reviewCode").value
  });
  document.getElementById("recordView").textContent =
    JSON.stringify(result.data, null, 2);
  document.getElementById("resultView").textContent =
    "HTTP " + result.status;
  if(result.status === 200 && result.data.record){
    loadedRecordKey = result.data.record.record_key;
  }
}
async function submitDecision(decision){
  if(!loadedRecordKey){
    document.getElementById("resultView").textContent =
      "先に最新候補を読み込んでください。";
    return;
  }
  const result = await postJson("/api/review/decision", {
    record_key: loadedRecordKey,
    decision,
    reason: document.getElementById("reason").value,
    review_code: document.getElementById("reviewCode").value
  });
  document.getElementById("resultView").textContent =
    "HTTP " + result.status + "\n" + JSON.stringify(result.data, null, 2);
  if(result.status === 200){
    loadedRecordKey = null;
  }
}
</script>
</body></html>"""
        )

    @bp.post("/api/review/latest")
    def review_latest():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({
                "status": "invalid_request",
                "reason": "json_object_required",
                "commerce_authorized": False,
            }), 400

        deps = resolve()
        if deps is None:
            return unavailable()
        records, reviews, configured_code = deps

        if not authorize(payload, configured_code):
            return jsonify({
                "status": "forbidden",
                "reason": "invalid_review_code",
                "commerce_authorized": False,
            }), 403

        identity_key = str(payload.get("identity_key") or "").strip()
        if not identity_key:
            return jsonify({
                "status": "invalid_request",
                "reason": "identity_key_required",
                "commerce_authorized": False,
            }), 400

        try:
            record = records.latest_for_identity(identity_key)
        except Exception:
            return jsonify({
                "status": "review_unavailable",
                "reason": "record_lookup_failed",
                "commerce_authorized": False,
            }), 503

        if record is None:
            return jsonify({
                "status": "not_found",
                "reason": "review_record_not_found",
                "commerce_authorized": False,
            }), 404

        try:
            existing = reviews.get_by_record_key(record["record_key"])
        except Exception:
            return jsonify({
                "status": "review_unavailable",
                "reason": "review_lookup_failed",
                "commerce_authorized": False,
            }), 503

        if existing is not None:
            return jsonify({
                "status": "already_reviewed",
                "reason": "record_already_reviewed",
                "review": existing,
                "commerce_authorized": False,
            }), 409

        eligibility = evaluate_review_eligibility(
            record,
            now=now_provider(),
            max_age_seconds=3600,
        )
        if eligibility["review_allowed"] is not True:
            return jsonify({
                "status": "review_blocked",
                "reason": "record_not_fresh",
                "freshness": eligibility["freshness"],
                "commerce_authorized": False,
            }), 409

        return jsonify({
            "version": API_VERSION,
            "status": "review_ready",
            "record": record,
            "freshness": eligibility["freshness"],
            "human_review_required": True,
            "commerce_authorized": False,
            "external_action_authorized": False,
        })

    @bp.post("/api/review/decision")
    def review_decision():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({
                "status": "invalid_request",
                "reason": "json_object_required",
                "commerce_authorized": False,
            }), 400

        deps = resolve()
        if deps is None:
            return unavailable()
        records, reviews, configured_code = deps

        if not authorize(payload, configured_code):
            return jsonify({
                "status": "forbidden",
                "reason": "invalid_review_code",
                "commerce_authorized": False,
            }), 403

        record_key = str(payload.get("record_key") or "").strip()
        decision = str(payload.get("decision") or "").strip().lower()
        reason = str(payload.get("reason") or "").strip()
        if not record_key or decision not in {"approve", "reject"} or not reason:
            return jsonify({
                "status": "invalid_request",
                "reason": "record_key_decision_reason_required",
                "commerce_authorized": False,
            }), 400

        try:
            record = records.get(record_key)
        except Exception:
            return jsonify({
                "status": "review_unavailable",
                "reason": "record_lookup_failed",
                "commerce_authorized": False,
            }), 503

        if record is None:
            return jsonify({
                "status": "not_found",
                "reason": "review_record_not_found",
                "commerce_authorized": False,
            }), 404

        try:
            if reviews.get_by_record_key(record_key) is not None:
                return jsonify({
                    "status": "already_reviewed",
                    "reason": "record_already_reviewed",
                    "commerce_authorized": False,
                }), 409
        except Exception:
            return jsonify({
                "status": "review_unavailable",
                "reason": "review_lookup_failed",
                "commerce_authorized": False,
            }), 503

        now = now_provider()
        try:
            audit = build_human_review_decision(
                record,
                decision=decision,
                reviewer_id="human",
                reason=reason,
                reviewed_at=now.isoformat(),
                now=now,
                max_age_seconds=3600,
            )
        except ValueError as exc:
            return jsonify({
                "status": "review_blocked",
                "reason": str(exc),
                "commerce_authorized": False,
            }), 409

        try:
            reviews.append(audit)
        except ValueError:
            return jsonify({
                "status": "already_reviewed",
                "reason": "record_already_reviewed",
                "commerce_authorized": False,
            }), 409
        except Exception:
            return jsonify({
                "status": "review_unavailable",
                "reason": "review_persistence_failed",
                "commerce_authorized": False,
            }), 503

        return jsonify({
            "version": API_VERSION,
            "status": "review_recorded",
            "decision": audit,
            "execution_triggered": False,
            "commerce_authorized": False,
            "external_action_authorized": False,
        })

    return bp


human_review_bp = create_human_review_blueprint()
