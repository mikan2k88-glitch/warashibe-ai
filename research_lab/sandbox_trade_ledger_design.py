"""Design an ephemeral trade ledger for Warashibe AI sandbox integration.

The ledger records proposed trades and simulated payment/settlement events
without touching production databases or moving real money.
"""

SANDBOX_TRADE_LEDGER_DESIGN_VERSION = "0.1"

ENTRY_TYPES = (
    "capital_reserve",
    "purchase_proposed",
    "payment_pending",
    "payment_succeeded",
    "payment_failed",
    "sale_recorded",
    "fee_recorded",
    "shipping_recorded",
    "refund_pending",
    "refund_succeeded",
    "refund_failed",
    "stop_loss_recorded",
    "realized_profit",
    "realized_loss",
)

REQUIRED_ENTRY_FIELDS = (
    "entry_id",
    "trade_id",
    "entry_type",
    "amount_jpy",
    "source",
)

MUTATION_POLICY = {
    "append_only": True,
    "overwrite_allowed": False,
    "delete_allowed": False,
    "production_write_allowed": False,
}


def validate_ledger_entry(entry):
    if not isinstance(entry, dict):
        return {
            "valid": False,
            "errors": ("entry_not_mapping",),
            "mutation_authorized": False,
        }

    errors = []
    for field in REQUIRED_ENTRY_FIELDS:
        if field not in entry:
            errors.append(f"missing_{field}")

    entry_type = entry.get("entry_type")
    if entry_type not in ENTRY_TYPES:
        errors.append("unsupported_entry_type")

    amount = entry.get("amount_jpy")
    if not isinstance(amount, int) or isinstance(amount, bool):
        errors.append("invalid_amount_jpy")

    entry_id = entry.get("entry_id")
    trade_id = entry.get("trade_id")
    if not isinstance(entry_id, str) or not entry_id.strip():
        errors.append("invalid_entry_id")
    if not isinstance(trade_id, str) or not trade_id.strip():
        errors.append("invalid_trade_id")

    return {
        "valid": not errors,
        "errors": tuple(errors),
        "mutation_authorized": False,
    }


def build_sandbox_trade_ledger_design():
    return {
        "version": SANDBOX_TRADE_LEDGER_DESIGN_VERSION,
        "mode": "ephemeral_sandbox_ledger",
        "entry_types": ENTRY_TYPES,
        "required_entry_fields": REQUIRED_ENTRY_FIELDS,
        "mutation_policy": dict(MUTATION_POLICY),
        "storage": "memory_or_ephemeral_file",
        "currency": "jpy",
        "append_only": True,
        "requires_idempotent_entry_id": True,
        "requires_trade_id": True,
        "requires_reconciliation": True,
        "requires_webhook_event_link": True,
        "requires_realized_profit_only_for_owner_reward": True,
        "production_database_write_authorized": False,
        "external_payment_authorized": False,
        "refund_execution_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
        "flow": (
            "validate_entry",
            "check_duplicate_entry_id",
            "append_ephemeral_entry",
            "recalculate_trade_balance",
            "reconcile_payment_events",
            "calculate_realized_pnl",
            "emit_sanitized_snapshot",
        ),
    }


def calculate_realized_pnl(entries):
    total = 0
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        entry_type = entry.get("entry_type")
        amount = entry.get("amount_jpy")
        if not isinstance(amount, int) or isinstance(amount, bool):
            continue
        if entry_type in ("sale_recorded", "refund_succeeded", "realized_profit"):
            total += amount
        elif entry_type in (
            "payment_succeeded",
            "fee_recorded",
            "shipping_recorded",
            "stop_loss_recorded",
            "realized_loss",
        ):
            total -= amount
    return total


def validate_sandbox_trade_ledger_design():
    design = build_sandbox_trade_ledger_design()
    assert design["mode"] == "ephemeral_sandbox_ledger"
    assert design["append_only"] is True
    assert design["requires_idempotent_entry_id"] is True
    assert design["requires_reconciliation"] is True
    assert design["production_database_write_authorized"] is False
    assert design["external_payment_authorized"] is False
    assert design["refund_execution_authorized"] is False
    assert design["commerce_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
