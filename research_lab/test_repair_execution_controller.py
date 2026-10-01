"""Targeted state-transition tests for the bounded repair execution controller."""
from research_lab.repair_execution_controller import control_repair_execution

A = "a" * 40
B = "b" * 40

PLANNING = {
    "recurrence_result": {"status": "recurrence_not_contained", "guardrail_effective": False},
    "repair_kind": "add_test",
    "target": "research_lab repair controller",
    "rationale": "prevent recurrence with one bounded regression test",
    "path": "research_lab/example.py",
    "change_summary": "add one targeted regression test",
    "expected_test": "research_lab.test_example",
}
WRITE = {"before_sha": A, "after_sha": B, "path": "research_lab/example.py",
         "expected_test": "research_lab.test_example"}


def main():
    planned = control_repair_execution(state="plan", planning=PLANNING)
    assert planned["controller_state"] == "write"
    assert planned["next_action"] == "execute_single_file_git_write"

    pending = control_repair_execution(state="write", write_evidence=WRITE)
    assert pending["status"] == "repair_controller_ci_pending"
    assert pending["next_action"] == "await_exact_sha_ci"

    unchanged = control_repair_execution(
        state="write", write_evidence=dict(WRITE, after_sha=A))
    assert unchanged["status"] == "repair_controller_hold"
    assert unchanged["next_action"] == "repair_write_evidence"

    complete = control_repair_execution(
        state="ci", write_evidence=WRITE,
        ci_evidence={"cycle_id": "cycle-controller", "repair_id": "repair-controller",
                     "observed_sha": B, "ci_status": "completed",
                     "ci_conclusion": "success"})
    assert complete["status"] == "repair_pipeline_complete"
    assert complete["controller_state"] == "complete"
    assert complete["milestone_reached"] is True
    assert complete["next_action"] == "advance_problem_queue"

    failed = control_repair_execution(
        state="ci", write_evidence=WRITE,
        ci_evidence={"cycle_id": "cycle-controller", "repair_id": "repair-controller",
                     "observed_sha": B, "ci_status": "completed",
                     "ci_conclusion": "failure"})
    assert failed["status"] == "repair_pipeline_failed"
    assert failed["next_action"] == "repair_current_problem"

    print("repair execution controller tests passed")


if __name__ == "__main__":
    main()
