"""Compose exact-SHA validation, audit, and ledger into one repair-cycle result.

Pure and fail-closed: no Git writes, retries, rollbacks, or external actions.
"""
from research_lab.problem_repair_validation_gate import evaluate_repair_validation
from research_lab.problem_repair_audit_record import build_repair_audit_record
from research_lab.problem_repair_ledger import build_repair_ledger


def finalize_repair_cycle(*, cycle_id, repair_id, before_sha, after_sha, path,
                          expected_test, observed_sha, ci_status, ci_conclusion):
    validation = evaluate_repair_validation(
        expected_sha=after_sha, observed_sha=observed_sha,
        ci_status=ci_status, ci_conclusion=ci_conclusion,
    )
    if validation["status"] not in {"repair_validated_success", "repair_validated_failure"}:
        return {"status": "repair_cycle_hold", "milestone_reached": False,
                "validation": validation, "audit": None, "ledger": None,
                "next_action": "await_exact_sha_ci"}

    audit = build_repair_audit_record(
        repair_id=repair_id, before_sha=before_sha, after_sha=after_sha,
        path=path, expected_test=expected_test, validation_result=validation,
    )
    if audit["status"] != "repair_audit_record_ready":
        return {"status": "repair_cycle_hold", "milestone_reached": False,
                "validation": validation, "audit": audit, "ledger": None,
                "next_action": "repair_audit_contract"}

    ledger = build_repair_ledger(cycle_id=cycle_id, records=[audit["audit_record"]])
    if ledger["status"] != "repair_ledger_ready":
        return {"status": "repair_cycle_hold", "milestone_reached": False,
                "validation": validation, "audit": audit, "ledger": ledger,
                "next_action": "repair_ledger_contract"}

    success = validation["repair_success"] is True
    return {"status": "repair_cycle_complete" if success else "repair_cycle_failed",
            "milestone_reached": success, "validation": validation,
            "audit": audit, "ledger": ledger,
            "next_action": "advance_problem_queue" if success else "repair_current_problem"}
