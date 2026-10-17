"""Read failed GitHub Actions job logs and produce a sanitized debug diagnosis."""
from __future__ import annotations
import json
import os
import re
import urllib.request
from dropship.auto_debug_diagnose import diagnose

API="https://api.github.com"
def fetch(url,token):
    req=urllib.request.Request(url,headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json","User-Agent":"warashibe-auto-debug"})
    with urllib.request.urlopen(req,timeout=20) as response:
        return response.read(250000).decode("utf-8","replace")
def analyze_run(repository,run_id,token):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",repository) or not str(run_id).isdigit() or not token:
        raise ValueError("invalid_parameters")
    jobs=json.loads(fetch(f"{API}/repos/{repository}/actions/runs/{run_id}/jobs?per_page=30",token))
    findings=[]
    for job in jobs.get("jobs",[])[:30]:
        if job.get("conclusion")!="failure":continue
        log=fetch(f"{API}/repos/{repository}/actions/jobs/{int(job['id'])}/logs",token)
        d=diagnose(log)
        findings.append({"job_id":int(job["id"]),"category":d["category"],"recommended_action":d["recommended_action"],"safe_to_retry":False})
    return {"status":"diagnosed" if findings else "no_failed_jobs","findings":findings[:10],"live_execution_allowed":False}
def main():
    result=analyze_run(os.environ["REPO"],os.environ["RUN_ID"],os.environ["GH_TOKEN"])
    with open("dropship-debug-diagnosis.json","w",encoding="utf-8") as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(result,ensure_ascii=False))
if __name__=="__main__":main()
