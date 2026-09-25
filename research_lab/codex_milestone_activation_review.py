"""Final offline review before any real Codex milestone execution.

This module verifies that the bounded Codex contract and supporting sandbox
components are present and internally valid. It never invokes Codex.
"""

from research_lab.codex_milestone_executor_design import (
    build_codex_milestone_contract,
    validate_codex_milestone_contract,
)
from research_lab.sandbox_external_integration_design import (
    validate_sandbox_external_integration_design,
)
from research_lab.sandbox_trade_ledger_design import (
    validate_sandbox_trade_ledger_design,
)
from research_lab.sandbox_market_data_adapter_design import (
    validate_sandbox_market_data_adapter_design,
)
from research_lab.sandbox_gemini_orchestrator_pipeline_design import (
    validate_sandbox_gemini_orchestrator_pipeline_design,
)
from research_lab.sandbox_stripe_ledger_bridge_design import (
    validate_sandbox_stripe_ledger_bridge_design,
)

CODEX_MILESTONE_ACTIVATION_REVIEW_VERSION = "0.1"


def run_codex_milestone_activation_review():
    checks = {
        "codex_contract_valid": validate_codex_milestone_contract() is True,
        "sandbox_external_integration_valid": (
            validate_sandbox_external_integration_design() is True
        ),
        "sandbox_trade_ledger_valid": (
            validate_sandbox_trade_ledger_design() is True
        ),
        "sandbox_market_data_adapter_valid": (
            validate_sandbox_market_data_adapter_design() is True
        ),
        "sandbox_gemini_orchestrator_valid": (
            validate_sandbox_gemini_orchestrator_pipeline_design() is True
        ),
        "sandbox_stripe_ledger_bridge_valid": (
            validate_sandbox_stripe_ledger_bridge_design() is True
        ),
    }

    contract = build_codex_milestone_contract()
    blockers = tuple(name for name, passed in checks.items() if not passed)

    ready = (
        not blockers
        and contract["allowed_branches"] == ("research-lab",)
        and contract["execution_limits"]["max_cycles"] == 10
        and contract["execution_limits"]["max_repairs_per_cycle"] == 1
        and contract["execution_limits"]["stop_on_human_gate"] is True
        and contract["codex_invocation_authorized"] is False
        and contract["network_execution_authorized"] is False
        and contract["commerce_authorized"] is False
        and contract["main_branch_change_authorized"] is False
    )

    return {
        "version": CODEX_MILESTONE_ACTIVATION_REVIEW_VERSION,
        "mode": "offline_activation_review",
        "checks": checks,
        "blockers": blockers,
        "ready_for_human_gate": ready,
        "next_required_action": (
            "request_explicit_codex_invocation_approval"
            if ready
            else "repair_activation_review_blockers"
        ),
        "codex_invocation_authorized": False,
        "network_execution_authorized": False,
        "secret_access_authorized": False,
        "commerce_authorized": False,
        "production_change_authorized": False,
        "main_branch_change_authorized": False,
        "external_action_authorized": False,
    }


def validate_codex_milestone_activation_review():
    review = run_codex_milestone_activation_review()
    assert review["ready_for_human_gate"] is True
    assert review["blockers"] == ()
    assert review["next_required_action"] == (
        "request_explicit_codex_invocation_approval"
    )
    assert review["codex_invocation_authorized"] is False
    assert review["network_execution_authorized"] is False
    assert review["secret_access_authorized"] is False
    assert review["commerce_authorized"] is False
    assert review["production_change_authorized"] is False
    assert review["main_branch_change_authorized"] is False
    assert review["external_action_authorized"] is False
    return True
