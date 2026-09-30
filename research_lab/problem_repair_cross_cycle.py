"""Cross-cycle continuity gate for AI repair ledgers.

Validates that adjacent research-lab repair cycles form one uninterrupted SHA
chain: previous.head_after must equal next.head_before. It also rejects duplicate
cycle IDs, duplicate repair IDs, malformed ledgers, and backward/self-links.

This module performs no Git writes, retries, rollbacks, or external actions.
"""


def validate_cross_cycle_continuity(ledgers):
    base = {
        "status": "hold_cross_cycle_continuity",
        "continuous": False,
        "checked_cycles": 0,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }

    if not isinstance(ledgers, (list, tuple)):
        return dict(base, reasons=("invalid_ledgers",))

    if len(ledgers) < 2:
        return dict(base, reasons=("insufficient_cycles",))

    cycle_ids = set()
    repair_ids = set()
    normalized = []

    for item in ledgers:
        if not isinstance(item, dict):
            return dict(base, reasons=("invalid_ledger",))

        required = ("cycle_id", "head_before", "head_after", "scope", "repair_ids")
        if any(k not in item for k in required):
            return dict(base, reasons=("invalid_ledger",))

        cycle_id = item.get("cycle_id")
        head_before = item.get("head_before")
        head_after = item.get("head_after")
        scope = item.get("scope")
        ids = item.get("repair_ids")

        if any(not isinstance(v, str) or not v.strip() for v in (cycle_id, head_before, head_after, scope)):
            return dict(base, reasons=("invalid_ledger",))

        if scope != "research-lab":
            return dict(base, reasons=("scope_not_allowed",))

        if not isinstance(ids, (list, tuple)) or len(ids) != 1:
            return dict(base, reasons=("repair_count_not_one",))

        repair_id = ids[0]
        if not isinstance(repair_id, str) or not repair_id.strip():
            return dict(base, reasons=("invalid_repair_id",))

        if cycle_id in cycle_ids:
            return dict(base, reasons=("duplicate_cycle_id",))

        if repair_id in repair_ids:
            return dict(base, reasons=("duplicate_repair_id",))

        if head_before == head_after:
            return dict(base, reasons=("self_linked_cycle",))

        cycle_ids.add(cycle_id)
        repair_ids.add(repair_id)
        normalized.append(
            {
                "cycle_id": cycle_id.strip(),
                "repair_id": repair_id.strip(),
                "head_before": head_before.strip(),
                "head_after": head_after.strip(),
            }
        )

    for previous, current in zip(normalized, normalized[1:]):
        if previous["head_after"] != current["head_before"]:
            return dict(
                base,
                checked_cycles=len(normalized),
                reasons=("sha_chain_mismatch",),
            )

    return dict(
        base,
        status="cross_cycle_continuity_ok",
        continuous=True,
        checked_cycles=len(normalized),
        reasons=(),
    )
