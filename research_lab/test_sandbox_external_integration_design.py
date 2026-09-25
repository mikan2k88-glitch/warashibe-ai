"""Tests for sandbox external integration design."""

from research_lab.sandbox_external_integration_design import (
    build_sandbox_external_integration_design,
    validate_sandbox_external_integration_design,
)


def run_tests():
    assert validate_sandbox_external_integration_design() is True

    design = build_sandbox_external_integration_design()
    assert design["components"] == (
        "gemini_orchestrator_driver",
        "market_data_adapter",
        "stripe_sandbox_adapter",
        "trade_ledger",
    )
    assert design["sandbox_only"] is True
    assert design["network_default"] == "deny"
    assert design["secret_default"] == "deny"
    assert design["ledger_default"] == "ephemeral"
    assert design["requires_idempotent_external_requests"] is True
    assert design["requires_failure_injection"] is True
    assert design["network_execution_authorized"] is False
    assert design["secret_read_authorized"] is False
    assert design["commerce_authorized"] is False
    assert design["production_change_authorized"] is False
    assert design["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("sandbox external integration design tests passed")
