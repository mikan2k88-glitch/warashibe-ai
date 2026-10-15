"""Collect prior sanitized GitHub Shadow artifacts, bounded and read-only."""
import io
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile
from dropship.v77_shadow_audit import summarize_observations

API = "https://api.github.com"

def _get(url, token, binary=False):
    request = Request(url, headers={"Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json", "X-GitHub-Api-Version":"2022-11-28",
        "User-Agent":"warashibe-shadow-readonly"})
    with urlopen(request, timeout=20) as response:
        data=response.read(300000)
    return data if binary else json.loads(data)

def collect(repository, token, *, max_runs=20):
    if not token or not repository or not 1 <= max_runs <= 30:
        raise ValueError("invalid_collector_configuration")
    runs=_get(f"{API}/repos/{repository}/actions/workflows/dropshipping-v70-shadow.yml/runs?per_page={max_runs}&status=completed",token)
    observations=[]
    for run in runs.get("workflow_runs", [])[:max_runs]:
        if run.get("conclusion") != "success":
            continue
        artifacts=_get(f"{API}/repos/{repository}/actions/runs/{int(run['id'])}/artifacts?per_page=20",token)
        for a in artifacts.get("artifacts",[]):
            if a.get("name") != "v70-shadow-observation" or a.get("expired") or a.get("size_in_bytes",0)>100000:
                continue
            zip_data=_get(f"{API}/repos/{repository}/actions/artifacts/{int(a['id'])}/zip",token,binary=True)
            with ZipFile(io.BytesIO(zip_data)) as archive:
                names=archive.namelist()
                if len(names)!=1 or not names[0].endswith("v70-shadow-observation.json"):
                    continue
                if archive.getinfo(names[0]).file_size>20000:
                    continue
                record=json.loads(archive.read(names[0]))
            observations.append(record)
            break
    return summarize_observations(observations)

def main():
    output=Path(os.environ.get("DROPSHIP_SHADOW_AUDIT_PATH","artifacts/v78-shadow-audit.json"))
    output.parent.mkdir(parents=True,exist_ok=True)
    try:
        result=collect(os.environ.get("GITHUB_REPOSITORY",""),os.environ.get("GH_TOKEN",""))
        result["collection_status"]="collected"
    except Exception as exc:
        result={"version":"7.8","collection_status":"unavailable",
                "error_kind":type(exc).__name__,"total_observations":0,
                "human_gate_ready":False,"live_execution_allowed":False}
    output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":
    main()
