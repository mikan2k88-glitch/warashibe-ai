"""Design the next milestone: sandbox external integration.

This module defines how Warashibe AI connects Gemini, Stripe Sandbox,
market-data adapters, and the internal ledger inside a bounded sandbox.
It grants no live commerce or production authority.
"""

SANDBOX_EXTERNAL_INTEGRATION_DESIGN_VERSION = "0.1"

INTEGRATION_COMPONENTS = (
    "gemini_orchestrator_driver",
    "market_data_adapter",
    "stripe_sandbox_adapter",
    "trade_ledger",
)

REQUIRED_GATES = (
    "network_gate",
    "secret_read_gate",
    "commerce_gate",
    "production_gate",
)

COMPONENT_POLICIES = {
    "gemini_orchestrator_driver": {
        "network_allowed_after_gate": True,
        "secret_read_required": True,
        "commerce_allowed": False,
        "production_allowed": False,
    },
    "market_data_adapter": {
        "network_allowed_after_gate": True,
        "secret_read_required": False,
        "commerce_allowed": False,
        "production_allowed": False,
    },
    "stripe_sandbox_adapter": {
        "network_allowed_after_gate": True,
        "secret_read_required": True,
        "commerce_allowed": False,
        "production_allowed": False,
    },
    "trade_ledger": {
        "network_allowed_after_gate": False,
        "secret_read_required": False,
        "commerce_allowed": False,
        "production_allowed": False,
    },
}


def build_sandbox_external_integration_design():
    return {
        "version": SANDBOX_EXTERNAL_INTEGRATION_DESIGN_VERSION,
        "mode": "design_only",
        "components": INTEGRATION_COMPONENTS,
        "required_gates": REQUIRED_GATES,
        "component_policies": COMPONENT_POLICIES,
        "sandbox_only": True,
        "disposable_execution_environment": True,
        "network_default": "deny",
        "secret_default": "deny",
        "ledger_default": "ephemeral",
        "requires_sanitized_observability": True,
        "requires_idempotent_external_requests": True,
        "requires_failure_injection": True,
        "requires_human_gate_for_network": True,
        "requires_human_gate_for_secret_read": True,
        "requires_human_gate_for_commerce": True,
        "requires_human_gate_for_production": True,
        "network_execution_authorized": False,
        "secret_read_authorized": False,
        "commerce_authorized": False,
        "production_change_authorized": False,
        "main_branch_change_authorized": False,
        "external_action_authorized": False,
        "flow": (
            "validate_component_contracts",
            "prepare_ephemeral_sandbox",
            "request_required_gates",
            "connect_selected_external_adapter",
            "capture_sanitized_result",
            "write_ephemeral_ledger_event",
            "inject_failure_cases",
            "compare_expected_behavior",
            "destroy_sandbox",
        ),
    }


def validate_sandbox_external_integration_design():
    design = build_sandbox_external_integration_design()
    assert design["sandbox_only"] is True
    assert design["disposable_execution_environment"] is True
    assert design["network_default"] == "deny"
    assert design["secret_default"] == "deny"
    assert design["ledger_default"] == "ephemeral"
    assert design["requires_failure_injection"] is True
    assert design["requires_human_gate_for_network"] is True
    assert design["requires_human_gate_for_secret_read"] is True
    assert design["requires_human_gate_for_commerce"] is True
    assert design["network_execution_authorized"] is False
    assert design["secret_read_authorized"] is False
    assert design["commerce_authorized"] is False
    assert design["production_change_authorized"] is False
    assert design["main_branch_change_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
