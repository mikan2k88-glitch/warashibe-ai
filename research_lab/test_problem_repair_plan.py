"""Targeted tests for the composed pre-write repair plan."""
from research_lab.problem_repair_plan import plan_repair_cycle


RECURRENCE = {
    "status": "recurrence_not_contained",
    "guardrail_effective": False,
}


def plan(**overrides):
    args = dict(
        recurrence_result=RECURRENCE,
        repair_kind="add_test",
        target="research_lab repair validation",
        rationale="prevent recurrence with a targeted regression test",
        path="research_lab/example.py",
        change_summary="add one targeted regression test",
        expected_test="research_lab.test_example",
    )
    args.update(overrides)
    return plan_repair_cycle(**args)


def main():
    ready = plan()
    assert ready["status"] == "repair_plan_ready"
    assert ready["next_action"] == "apply_bounded_git_write"
    assert ready["candidate"]["status"] == "repair_candidate_reviewable"
    assert ready["ai_decision"]["status"] == "ai_repair_authorized"
    assert ready["execution"]["status"] == "repair_execution_plan_ready"
    assert ready["execution"]["git_write_authorized"] is True
    assert ready["execution"]["plan"]["branch"] == "research-lab"
    assert ready["execution"]["plan"]["single_file_only"] is True
    assert ready["execution"]["plan"]["requires_same_sha_ci_after_write"] is True

    blocked_candidate = plan(repair_kind="unknown")
    assert blocked_candidate["status"] == "repair_plan_hold"
    assert blocked_candidate["next_action"] == "repair_candidate"
    assert blocked_candidate["ai_decision"] is None

    blocked_scope = plan(target="production payment")
    assert blocked_scope["status"] == "repair_plan_hold"
    assert blocked_scope["next_action"] == "repair_candidate"

    blocked_execution = plan(path="../example.py")
    assert blocked_execution["status"] == "repair_plan_hold"
    assert blocked_execution["next_action"] == "repair_execution_boundary"
    assert blocked_execution["execution"]["git_write_authorized"] is False

    print("problem repair plan tests passed")


if __name__ == "__main__":
    main()
