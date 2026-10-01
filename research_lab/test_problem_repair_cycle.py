"""Targeted tests for the composed problem repair cycle."""
from research_lab.problem_repair_cycle import finalize_repair_cycle

BEFORE = "a" * 40
AFTER = "b" * 40


def cycle(**overrides):
    args = dict(
        cycle_id="cycle-1", repair_id="repair-1", before_sha=BEFORE,
        after_sha=AFTER, path="research_lab/example.py",
        expected_test="research_lab.test_example", observed_sha=AFTER,
        ci_status="completed", ci_conclusion="success",
    )
    args.update(overrides)
    return finalize_repair_cycle(**args)


def main():
    success = cycle()
    assert success["status"] == "repair_cycle_complete"
    assert success["milestone_reached"] is True
    assert success["next_action"] == "advance_problem_queue"
    assert success["audit"]["status"] == "repair_audit_record_ready"
    assert success["ledger"]["status"] == "repair_ledger_ready"

    pending = cycle(ci_status="in_progress", ci_conclusion=None)
    assert pending["status"] == "repair_cycle_hold"
    assert pending["next_action"] == "await_exact_sha_ci"
    assert pending["audit"] is None and pending["ledger"] is None

    mismatch = cycle(observed_sha="c" * 40)
    assert mismatch["status"] == "repair_cycle_hold"
    assert mismatch["next_action"] == "await_exact_sha_ci"
    assert mismatch["audit"] is None and mismatch["ledger"] is None

    failed = cycle(ci_conclusion="failure")
    assert failed["status"] == "repair_cycle_failed"
    assert failed["milestone_reached"] is False
    assert failed["next_action"] == "repair_current_problem"
    assert failed["audit"]["status"] == "repair_audit_record_ready"
    assert failed["ledger"]["status"] == "repair_ledger_ready"

    print("problem repair cycle tests passed")


if __name__ == "__main__":
    main()
