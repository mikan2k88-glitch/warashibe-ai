"""v8.3 conservative fix proposal builder. No code changes are applied here."""
from __future__ import annotations

ALLOWED_WORKFLOW = ".github/workflows/dropshipping-shadow-collect.yml"
OLD_COMMAND = "run: python scripts/dropship_shadow_collect.py"
NEW_COMMAND = "run: PYTHONPATH=. python -m scripts.dropship_shadow_collect"

def suggest_repair(diagnosis: dict, files: dict[str, str]) -> dict:
    """Only propose a deterministic, narrow patch for a previously understood import failure."""
    base = {"version":"8.3","status":"no_safe_fix_identified",
            "requires_ci":True,"requires_human_or_guarded_merge":True,
            "live_execution_allowed":False,"files":[]}
    if not isinstance(diagnosis,dict) or not isinstance(files,dict):
        return base
    findings = diagnosis.get("findings")
    if not isinstance(findings,list) or not any(
        isinstance(item,dict) and item.get("category")=="python_import" for item in findings
    ):
        return base
    content=files.get(ALLOWED_WORKFLOW)
    if not isinstance(content,str) or content.count(OLD_COMMAND)!=1:
        return base
    changed=content.replace(OLD_COMMAND,NEW_COMMAND,1)
    return {**base,"status":"proposal_ready",
            "fix_id":"shadow_collect_import_path",
            "reason":"known_safe_workflow_import_path_fix",
            "files":[{"path":ALLOWED_WORKFLOW,"before":content,"after":changed}]}
