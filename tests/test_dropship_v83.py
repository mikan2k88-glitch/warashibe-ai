from dropship.v83_repair_proposals import suggest_repair, ALLOWED_WORKFLOW, OLD_COMMAND, NEW_COMMAND
def test_known_import_failure_proposes_exact_scoped_fix():
    original="name: Test\nsteps:\n  - "+OLD_COMMAND+"\n"
    result=suggest_repair({"findings":[{"category":"python_import"}]},{ALLOWED_WORKFLOW:original})
    assert result["status"]=="proposal_ready"
    assert result["files"][0]["path"]==ALLOWED_WORKFLOW
    assert NEW_COMMAND in result["files"][0]["after"]
    assert result["live_execution_allowed"] is False
def test_unknown_error_never_generates_patch():
    assert suggest_repair({"findings":[{"category":"cj_rate_limit"}]},{ALLOWED_WORKFLOW:OLD_COMMAND})["files"]==[]
def test_changed_workflow_fails_closed():
    assert suggest_repair({"findings":[{"category":"python_import"}]},{ALLOWED_WORKFLOW:NEW_COMMAND})["status"]=="no_safe_fix_identified"
def test_duplicate_commands_fail_closed():
    assert suggest_repair({"findings":[{"category":"python_import"}]},{ALLOWED_WORKFLOW:OLD_COMMAND+"\n"+OLD_COMMAND})["files"]==[]
