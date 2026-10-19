"""Read failed GitHub Actions job logs and produce a sanitized debug diagnosis."""
from __future__ import annotations
import json
import os
import re
import urllib.request
from urllib.error import HTTPError
from dropship.auto_debug_diagnose import diagnose
from dropship.v83_repair_proposals import suggest_repair, ALLOWED_WORKFLOW
from pathlib import Path

API="https://api.github.com"
def fetch(url,token):
    req=urllib.request.Request(url,headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json","User-Agent":"warashibe-auto-debug"})
    try:
        with urllib.request.urlopen(req,timeout=20) as response:
            return response.read(250000).decode("utf-8","replace")
    except HTTPError as exc:
        raise RuntimeError(f"github_http_{exc.code}") from None
def analyze_run(repository,run_id,token):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",repository) or not str(run_id).isdigit() or not token:
        raise ValueError("invalid_parameters")
    jobs=json.loads(fetch(f"{API}/repos/{repository}/actions/runs/{run_id}/jobs?per_page=30",token))
    findings=[]
    for job in jobs.get("jobs",[])[:30]:
        if job.get("conclusion")!="failure":continue
        try:
            log=fetch(f"{API}/repos/{repository}/actions/jobs/{int(job['id'])}/logs",token)
            d=diagnose(log)
        except Exception:
            d={"category":"logs_unavailable","recommended_action":"inspect_github_run_in_browser"}
        findings.append({"job_id":int(job["id"]),"category":d["category"],"recommended_action":d["recommended_action"],"safe_to_retry":False})
    return {"status":"diagnosed" if findings else "no_failed_jobs","findings":findings[:10],"live_execution_allowed":False}
def main():
    try:
        result=analyze_run(os.environ["REPO"],os.environ["RUN_ID"],os.environ["GH_TOKEN"])
    except Exception:
        result={"status":"diagnosis_unavailable","findings":[], "live_execution_allowed":False}
    with open("dropship-debug-diagnosis.json","w",encoding="utf-8") as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
    workflow=Path(ALLOWED_WORKFLOW)
    proposal=suggest_repair(result,{ALLOWED_WORKFLOW:workflow.read_text(encoding="utf-8")} if workflow.is_file() else {})
    # No repository patches or raw workflow contents are included in public artifacts.
    metadata={key:value for key,value in proposal.items() if key!="files"}
    metadata["changed_paths"]=[entry["path"] for entry in proposal["files"]]
    Path("dropship-debug-repair-proposal.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    print(json.dumps(metadata,ensure_ascii=False))
if __name__=="__main__":main()
