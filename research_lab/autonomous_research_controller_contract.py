"""Explicit contract for the autonomous research snapshot controller.

The contract documents which controller outcomes may continue local research
planning and which must stop or wait. It never executes the resulting action.
"""

CONTROLLER_CONTRACT_VERSION = "0.1"

DECISION_PERMISSIONS = {
    "proceed": {
        "may_prepare_research_change": True,
        "may_prepare_repair": False,
        "must_wait": False,
        "must_stop": False,
    },
    "repair": {
        "may_prepare_research_change": False,
        "may_prepare_repair": True,
        "must_wait": False,
        "must_stop": False,
    },
    "wait": {
        "may_prepare_research_change": False,
        "may_prepare_repair": False,
        "must_wait": True,
        "must_stop": False,
    },
    "stop": {
        "may_prepare_research_change": False,
        "may_prepare_repair": False,
        "must_wait": False,
        "must_stop": True,
    },
}

ALWAYS_FORBIDDEN = (
    "modify_main_branch",
    "execute_supabase_ddl",
    "change_secrets_or_credentials",
    "change_billing_or_paid_plan",
    "change_external_production_config",
    "purchase_real_item",
    "sell_real_item",
    "execute_payment",
)


def controller_contract(decision):
    if decision not in DECISION_PERMISSIONS:
        raise ValueError("unsupported controller decision")
    return {
        "version": CONTROLLER_CONTRACT_VERSION,
        "decision": decision,
        **DECISION_PERMISSIONS[decision],
        "forbidden_actions": ALWAYS_FORBIDDEN,
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_controller_contract():
    proceed = controller_contract("proceed")
    assert proceed["may_prepare_research_change"] is True
    assert proceed["external_action_authorized"] is False
    for decision in ("repair", "wait", "stop"):
        assert controller_contract(decision)["may_prepare_research_change"] is False
    return True
