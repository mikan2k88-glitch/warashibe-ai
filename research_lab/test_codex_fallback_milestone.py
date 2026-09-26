from research_lab.codex_fallback_milestone import assess_milestone

SHA = "1c0f10c9a893646fd5f065a8c8ff84fe59e1b2bc"


def main():
    base = dict(branch="research-lab", commit_sha=SHA,
                research_ci="success", focused_ci="success")
    result = assess_milestone(**base)
    assert result["status"] == "verified"
    assert result["main_promotion_authorized"] is False
    assert result["external_action_invoked"] is False

    for change, blocker in (
        ({"branch": "main"}, "lab_only"),
        ({"commit_sha": ""}, "commit_present"),
        ({"research_ci": "queued"}, "research_ci_success"),
        ({"focused_ci": "failure"}, "focused_ci_success"),
        ({"main_changed": True}, "main_untouched"),
        ({"production_changed": True}, "production_untouched"),
        ({"real_db_write": True}, "real_db_write_absent"),
    ):
        assert blocker in assess_milestone(**(base | change))["blockers"]
        assert assess_milestone(**(base | change))["status"] == "pending_or_blocked"
    print("Codex fallback milestone gate: PASS")


if __name__ == "__main__":
    main()
