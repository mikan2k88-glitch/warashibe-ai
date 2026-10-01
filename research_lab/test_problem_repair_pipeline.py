"""End-to-end targeted tests for the bounded repair pipeline."""
from research_lab.problem_repair_pipeline import advance_repair_pipeline

A = "a" * 40
B = "b" * 40

PLANNING = {
    "recurrence_result": {"status": "recurrence_not_contained", "guardrail_effective": False},
    "repair_kind": "add_test",
    "target": "research_lab repair validation",
    "rationale": "prevent recurrence with one targeted test",
    "path": "research_lab/example.py",
    "change_summary": "add one targeted regression test",
    "expected_test": "research_lab.test_example",
}

VERIFICATION = {
    "cycle_id": "cycle-e2e",
    "repair_id": "repair-e2e",
    "before_sha": A,
    "after_sha": B,
    "path": "research_lab/example.py",
    "expected_test": "research_lab.test_example",
    "observed_sha": B,
    "ci_status": "completed",
    "ci_conclusion": "success",
}


def main():
    planned = advance_repair_pipeline(phase="plan", planning=PLANNING)
    assert planned["status"] == "repair_pipeline_write_ready"
    assert planned["phase"] == "write"
    assert planned["milestone_reached"] is False
    assert planned["execution_plan"]["branch"] == "research-lab"
    assert planned["execution_plan"]["requires_same_sha_ci_after_write"] is True

    complete = advance_repair_pipeline(phase="verify", verification=VERIFICATION)
    assert complete["status"] == "repair_pipeline_complete"
    assert complete["phase"] == "complete"
    assert complete["milestone_reached"] is True
    assert complete["result"]["audit"]["status"] == "repair_audit_record_ready"
    assert complete["result"]["ledger"]["status"] == "repair_ledger_ready"
    assert complete["next_action"] == "advance_problem_queue"

    mismatch = dict(VERIFICATION, observed_sha="c" * 40)
    held = advance_repair_pipeline(phase="verify", verification=mismatch)
    assert held["status"] == "repair_pipeline_hold"
    assert held["milestone_reached"] is False
    assert held["next_action"] == "await_exact_sha_ci"

    failure = dict(VERIFICATION, ci_conclusion="failure")
    failed = advance_repair_pipeline(phase="verify", verification=failure)
    assert failed["status"] == "repair_pipeline_failed"
    assert failed["next_action"] == "repair_current_problem"

    print("problem repair pipeline end-to-end tests passed")


if __name__ == "__main__":
    main()
