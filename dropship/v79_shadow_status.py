"""v7.9 dashboard observation freshness via read-only GitHub metadata."""
import json
from urllib.request import Request, urlopen
from flask import Blueprint, jsonify

v79_bp=Blueprint("dropship_v79",__name__,url_prefix="/dropship/v7.9")
RUNS="https://api.github.com/repos/mikan2k88-glitch/warashibe-ai/actions/runs?per_page=30"
TARGET="Dropshipping v7 Shadow Evidence"

def latest_shadow(fetch=None):
    if fetch is None:
        def fetch():
            req=Request(RUNS,headers={"Accept":"application/vnd.github+json","User-Agent":"warashibe-public-readonly"})
            with urlopen(req,timeout=5) as response:
                return json.load(response)
    try:
        rows=fetch().get("workflow_runs",[])
        matched=next((r for r in rows if r.get("name")==TARGET),None)
        if not matched:
            raise ValueError("shadow_run_not_found")
        run_id=matched.get("id")
        return {"status":"observed","run_status":matched.get("status"),
                "run_conclusion":matched.get("conclusion"),
                "observed_at":matched.get("created_at"),
                "run_url":f"https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/{int(run_id)}",
                "artifact_evidence":"review_in_github_actions",
                "operational_acceptance":"pending"}
    except Exception:
        return {"status":"unavailable","run_status":"unknown","run_conclusion":None,
                "observed_at":None,"run_url":None,
                "artifact_evidence":"unknown","operational_acceptance":"pending"}

@v79_bp.get("/status")
def status():
    result=latest_shadow()
    return jsonify({"version":"7.9",**result,"human_gate_ready":False,
                    "live_execution_allowed":False})
