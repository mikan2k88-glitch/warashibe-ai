"""Read-only bridge from the public GitHub Actions API to the lab dashboard."""

import json
import time
from urllib.request import Request, urlopen

API = "https://api.github.com/repos/mikan2k88-glitch/warashibe-ai/actions/runs?branch=research-lab&per_page=20"
CACHE_SECONDS = 300
_cache = {"at": 0.0, "runs": []}


def workflow_runs():
    now = time.time()
    if _cache["runs"] and now - _cache["at"] < CACHE_SECONDS:
        return _cache["runs"]
    request = Request(API, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "warashibe-ai-research-lab",
    })
    try:
        with urlopen(request, timeout=4) as response:
            payload = json.load(response)
        runs = [
            {
                "run_number": x["run_number"],
                "title": x["display_title"],
                "status": x["status"],
                "conclusion": x.get("conclusion"),
                "created_at": x["created_at"],
                "updated_at": x["updated_at"],
                "sha": x["head_sha"][:8],
            }
            for x in payload.get("workflow_runs", [])
        ]
        _cache.update(at=now, runs=runs)
        return runs
    except Exception:
        return _cache["runs"]


def live_snapshot(stage, next_theme, total_checks):
    runs = workflow_runs()
    if not runs:
        return None
    latest = runs[0]
    passed = total_checks if latest["conclusion"] == "success" else 0
    return {
        "status": "passed" if latest["conclusion"] == "success" else latest["status"],
        "stage": stage,
        "next_theme": next_theme,
        "generated_at": latest["updated_at"],
        "passed_checks": passed,
        "total_checks": total_checks,
        "check_percent": round(100 * passed / total_checks) if total_checks else 0,
        "source": "github_actions",
        "run_number": latest["run_number"],
    }
