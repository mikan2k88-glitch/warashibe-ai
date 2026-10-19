"""v8.4 fail-closed local validation and patch generation for known fixes."""
from __future__ import annotations
import difflib
from dropship.v83_repair_proposals import suggest_repair, ALLOWED_WORKFLOW

def validate_and_diff(diagnosis, files):
    proposal = suggest_repair(diagnosis, files)
    result = {"version":"8.4","status":"blocked","patch":"","changed_paths":[],
              "apply_to_main":False,"auto_merge":False,"live_execution_allowed":False}
    if proposal["status"]!="proposal_ready" or len(proposal["files"])!=1:
        return result
    item=proposal["files"][0]
    if item["path"]!=ALLOWED_WORKFLOW or item["before"]!=files.get(ALLOWED_WORKFLOW):
        return result
    if item["before"]==item["after"] or len(item["before"])>20000:
        return result
    patch="".join(difflib.unified_diff(
        item["before"].splitlines(keepends=True),
        item["after"].splitlines(keepends=True),
        fromfile="a/"+ALLOWED_WORKFLOW,tofile="b/"+ALLOWED_WORKFLOW))
    return {**result,"status":"patch_validated","patch":patch,
            "changed_paths":[ALLOWED_WORKFLOW]}
