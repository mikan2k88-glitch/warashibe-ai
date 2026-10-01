"""Targeted state-transition tests for the bounded repair execution controller.

This file also serves as the safe single-file live-write probe for Improvement 001.
The probe completed on exact-SHA CI #1025 before milestone finalization.
"""
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

    live = control_repair_execution(
        state="ci",
        write_evidence={"before_sha": "5b4e490325ea4816df86b8a658c1528ff8785998",
                        "after_sha": "5412354e4610e344b904b4a3ffdeb352f5f4edcd",
                        "path": "research_lab/repair_execution_controller.py",
                        "expected_test": "research_lab.test_repair_execution_controller"},
        ci_evidence={"cycle_id": "p0-live-1027", "repair_id": "exact-sha-finalization",
                     "observed_sha": "5412354e4610e344b904b4a3ffdeb352f5f4edcd",
                     "ci_status": "completed", "ci_conclusion": "success"})
    assert live["status"] == "repair_pipeline_complete"
    assert live["milestone_reached"] is True
    assert live["next_action"] == "advance_problem_queue"
    assert live["result"]["audit"]["status"] == "repair_audit_record_ready"
    assert live["result"]["ledger"]["status"] == "repair_ledger_ready"

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
