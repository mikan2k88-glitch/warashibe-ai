"""Classify sanitized GitHub Actions failures without leaking log content."""
import re
def diagnose(text):
    text=str(text)[-120000:]
    rules=[
        ("python_import",r"ModuleNotFoundError|ImportError", "inspect_module_import_path"),
        ("cj_rate_limit",r"(?:429.{0,90}cjdropshipping|cjdropshipping.{0,90}429|HTTP 429)", "respect_retry_after_and_reuse_token"),
        ("test_assertion",r"AssertionError|FAILED tests/", "inspect_failed_test_and_code"),
        ("dependency",r"No matching distribution found|ResolutionImpossible", "review_dependency_constraints"),
        ("syntax",r"SyntaxError|IndentationError", "fix_syntax_on_branch"),
    ]
    for category,pattern,action in rules:
        if re.search(pattern,text,re.I):
            return {"category":category,"recommended_action":action,"safe_to_retry":False}
    return {"category":"unclassified","recommended_action":"manual_or_agent_triage","safe_to_retry":False}
