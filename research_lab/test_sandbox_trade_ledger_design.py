"""Tests for sandbox trade ledger design."""

from research_lab.sandbox_trade_ledger_design import (
    build_sandbox_trade_ledger_design,
    calculate_realized_pnl,
    validate_ledger_entry,
    validate_sandbox_trade_ledger_design,
)


def run_tests():
    assert validate_sandbox_trade_ledger_design() is True

    valid = validate_ledger_entry({
        "entry_id": "evt-001",
        "trade_id": "trade-001",
        "entry_type": "payment_succeeded",
        "amount_jpy": 3000,
        "source": "stripe_sandbox",
    })
    assert valid["valid"] is True
    assert valid["mutation_authorized"] is False

    invalid = validate_ledger_entry({
        "entry_id": "",
        "trade_id": "trade-001",
        "entry_type": "unknown",
        "amount_jpy": "3000",
        "source": "fixture",
    })
    assert invalid["valid"] is False

    entries = [
        {"entry_type": "payment_succeeded", "amount_jpy": 3000},
        {"entry_type": "sale_recorded", "amount_jpy": 4500},
        {"entry_type": "fee_recorded", "amount_jpy": 450},
        {"entry_type": "shipping_recorded", "amount_jpy": 210},
    ]
    assert calculate_realized_pnl(entries) == 840

    design = build_sandbox_trade_ledger_design()
    assert design["storage"] == "memory_or_ephemeral_file"
    assert design["append_only"] is True
    assert design["production_database_write_authorized"] is False
    assert design["external_payment_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("sandbox trade ledger design tests passed")
