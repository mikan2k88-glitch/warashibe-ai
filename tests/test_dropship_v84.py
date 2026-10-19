from dropship.v84_patch_validation import validate_and_diff
from dropship.v83_repair_proposals import ALLOWED_WORKFLOW, OLD_COMMAND, NEW_COMMAND

def test_known_fix_produces_one_allowed_patch():
    content="name: Shadow\n  "+OLD_COMMAND+"\n"
    r=validate_and_diff({"findings":[{"category":"python_import"}]},{ALLOWED_WORKFLOW:content})
    assert r["status"]=="patch_validated"
    assert "-  "+OLD_COMMAND in r["patch"]
    assert "+  "+NEW_COMMAND in r["patch"]
    assert r["auto_merge"] is False and r["live_execution_allowed"] is False

def test_unknown_error_produces_no_patch():
    r=validate_and_diff({"findings":[{"category":"cj_rate_limit"}]},{ALLOWED_WORKFLOW:OLD_COMMAND})
    assert r["status"]=="blocked" and r["patch"]==""

def test_already_repaired_never_writes():
    r=validate_and_diff({"findings":[{"category":"python_import"}]},{ALLOWED_WORKFLOW:NEW_COMMAND})
    assert r["status"]=="blocked" and not r["changed_paths"]
