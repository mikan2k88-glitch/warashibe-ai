"""Codex-free LAB milestone acceptance; pure logic, no external actions."""

def assess_milestone(*, branch, commit_sha, research_ci, focused_ci,
                     main_changed=False, production_changed=False,
                     real_db_write=False):
    checks = {
        "lab_only": branch == "research-lab",
        "commit_present": isinstance(commit_sha, str) and len(commit_sha) == 40
                          and all(c in "0123456789abcdef" for c in commit_sha),
        "research_ci_success": research_ci == "success",
        "focused_ci_success": focused_ci == "success",
        "main_untouched": main_changed is False,
        "production_untouched": production_changed is False,
        "real_db_write_absent": real_db_write is False,
    }
    blockers = [name for name, passed in checks.items() if not passed]
    return {
        "status": "verified" if not blockers else "pending_or_blocked",
        "checks": checks,
        "blockers": blockers,
        "codex_required": False,
        "main_promotion_authorized": False,
        "external_action_invoked": False,
    }
