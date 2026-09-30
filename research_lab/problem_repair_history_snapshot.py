"""Build an auditable snapshot of contiguous AI repair history.

The snapshot summarizes a validated sequence of research-lab repair ledgers into
fixed counts and boundary SHAs. It performs no Git writes, retries, rollbacks, or
external runtime actions.
"""

from research_lab.problem_repair_cross_cycle import validate_cross_cycle_continuity


def build_repair_history_snapshot(ledgers):
    base = {
        "status": "hold_repair_history_snapshot",
        "snapshot": None,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }

    continuity = validate_cross_cycle_continuity(ledgers)
    if continuity.get("status") != "cross_cycle_continuity_ok":
        return dict(base, reasons=("continuity_not_validated",))

    normalized = []
    success_count = 0
    failure_count = 0

    for ledger in ledgers:
        records = ledger.get("records")
        if not isinstance(records, (list, tuple)) or len(records) != 1:
            return dict(base, reasons=("invalid_ledger_records",))

        record = records[0]
        if not isinstance(record, dict):
            return dict(base, reasons=("invalid_ledger_records",))

        validation_status = record.get("validation_status")
        if validation_status == "repair_validated_success":
            success_count += 1
        elif validation_status == "repair_validated_failure":
            failure_count += 1
        else:
            return dict(base, reasons=("validation_not_terminal",))

        normalized.append(
            {
                "cycle_id": ledger["cycle_id"],
                "repair_id": ledger["repair_ids"][0],
                "head_before": ledger["head_before"],
                "head_after": ledger["head_after"],
                "validation_status": validation_status,
            }
        )

    snapshot = {
        "scope": "research-lab",
        "cycle_count": len(normalized),
        "repair_count": len(normalized),
        "success_count": success_count,
        "failure_count": failure_count,
        "head_start": normalized[0]["head_before"],
        "head_end": normalized[-1]["head_after"],
        "continuous": True,
        "cycles": tuple(normalized),
    }

    return dict(
        base,
        status="repair_history_snapshot_ready",
        snapshot=snapshot,
        reasons=(),
    )
