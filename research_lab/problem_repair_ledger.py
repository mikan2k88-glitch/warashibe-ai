"""Fail-closed ledger gate for one AI repair per research cycle.

The ledger accepts reproducible repair audit records and prevents duplicate repair
IDs, multiple repairs in one cycle, and broken before/after SHA continuity.
It never edits code, retries work, rolls back changes, or authorizes external
runtime actions.
"""


def build_repair_ledger(*, cycle_id, records):
    base = {
        "status": "hold_repair_ledger",
        "ledger": None,
        "cycle_closed": True,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }

    if not isinstance(cycle_id, str) or not cycle_id.strip():
        return dict(base, reasons=("invalid_cycle_id",))

    if not isinstance(records, (list, tuple)):
        return dict(base, reasons=("invalid_records",))

    if len(records) == 0:
        return dict(base, reasons=("empty_cycle",))

    if len(records) > 1:
        return dict(base, reasons=("multiple_repairs_in_cycle",))

    record = records[0]
    if not isinstance(record, dict):
        return dict(base, reasons=("invalid_record",))

    required = (
        "repair_id",
        "before_sha",
        "after_sha",
        "path",
        "expected_test",
        "validation_status",
        "scope",
    )
    if any(not isinstance(record.get(k), str) or not record.get(k).strip() for k in required):
        return dict(base, reasons=("invalid_record",))

    if record.get("scope") != "research-lab":
        return dict(base, reasons=("scope_not_allowed",))

    if record.get("single_file_only") is not True:
        return dict(base, reasons=("single_file_limit_missing",))

    if record["before_sha"] == record["after_sha"]:
        return dict(base, reasons=("sha_not_changed",))

    if record["validation_status"] not in {
        "repair_validated_success",
        "repair_validated_failure",
    }:
        return dict(base, reasons=("validation_not_terminal",))

    ledger = {
        "cycle_id": cycle_id.strip(),
        "repair_count": 1,
        "repair_ids": (record["repair_id"].strip(),),
        "head_before": record["before_sha"].strip(),
        "head_after": record["after_sha"].strip(),
        "records": (dict(record),),
        "scope": "research-lab",
        "single_repair_cycle": True,
    }

    return dict(
        base,
        status="repair_ledger_ready",
        ledger=ledger,
        reasons=(),
    )


def append_repair_to_ledger(ledger_result, audit_record):
    base = {
        "status": "hold_repair_ledger_append",
        "ledger": None,
        "cycle_closed": True,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }

    if not isinstance(ledger_result, dict) or ledger_result.get("status") != "repair_ledger_ready":
        return dict(base, reasons=("ledger_not_ready",))

    ledger = ledger_result.get("ledger")
    if not isinstance(ledger, dict):
        return dict(base, reasons=("invalid_ledger",))

    if not isinstance(audit_record, dict):
        return dict(base, reasons=("invalid_record",))

    repair_id = audit_record.get("repair_id")
    if isinstance(repair_id, str) and repair_id in ledger.get("repair_ids", ()):
        return dict(base, reasons=("duplicate_repair_id",))

    before_sha = audit_record.get("before_sha")
    if isinstance(before_sha, str) and before_sha != ledger.get("head_after"):
        return dict(base, reasons=("sha_chain_mismatch",))

    return dict(base, reasons=("multiple_repairs_in_cycle",))
