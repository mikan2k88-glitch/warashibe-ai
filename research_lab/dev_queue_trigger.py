import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from flask import Blueprint, jsonify


dev_queue_trigger_bp = Blueprint("dev_queue_trigger", __name__)

_SUPABASE_TABLE = "warashibe_dev_queue"
_GITHUB_REPO = "mikan2k88-glitch/warashibe-ai"
_GITHUB_WORKFLOW = "research-lab-schedule.yml"
_GITHUB_REF = "main"
_COOLDOWN_SECONDS = 10
_last_dispatch_at = 0.0


def _supabase_headers():
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
        or os.environ.get("SUPABASE_ANON_KEY")
    )
    if not key:
        raise RuntimeError("supabase_key_not_configured")
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
    }


def _has_pending_task():
    base_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    if not base_url:
        raise RuntimeError("supabase_url_not_configured")

    query = urllib.parse.urlencode(
        {
            "status": "eq.pending",
            "select": "task_id",
            "order": "id.asc",
            "limit": "1",
        }
    )
    request = urllib.request.Request(
        f"{base_url}/rest/v1/{_SUPABASE_TABLE}?{query}",
        headers=_supabase_headers(),
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        rows = json.loads(response.read().decode("utf-8"))
    return bool(rows)


def _dispatch_github():
    token = os.environ.get("GITHUB_TRIGGER_TOKEN")
    if not token:
        raise RuntimeError("github_trigger_token_not_configured")

    url = (
        f"https://api.github.com/repos/{_GITHUB_REPO}"
        f"/actions/workflows/{_GITHUB_WORKFLOW}/dispatches"
    )
    body = json.dumps({"ref": _GITHUB_REF}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "warashibe-ai-trigger",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        if response.status not in (204, 201, 200):
            raise RuntimeError(f"github_dispatch_status_{response.status}")


def _dispatch_with_retry():
    delays = (0, 1, 3)
    last_error = None
    for delay in delays:
        if delay:
            time.sleep(delay)
        try:
            _dispatch_github()
            return
        except (urllib.error.URLError, urllib.error.HTTPError, RuntimeError) as exc:
            last_error = exc
    raise RuntimeError(f"github_dispatch_failed:{last_error}")


@dev_queue_trigger_bp.route("/internal/dev-queue/wake", methods=["POST"])
def wake_dev_queue():
    global _last_dispatch_at

    try:
        if not _has_pending_task():
            return jsonify({"status": "ignored", "reason": "no_pending_task"}), 202

        now = time.monotonic()
        if now - _last_dispatch_at < _COOLDOWN_SECONDS:
            return jsonify({"status": "ignored", "reason": "cooldown"}), 202

        _dispatch_with_retry()
        _last_dispatch_at = now
        return jsonify({"status": "dispatched"}), 202
    except RuntimeError as exc:
        return jsonify({"status": "error", "reason": str(exc)}), 503
    except Exception:
        return jsonify({"status": "error", "reason": "unexpected_error"}), 503
