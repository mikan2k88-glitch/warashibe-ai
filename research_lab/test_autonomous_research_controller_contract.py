"""Offline tests for the autonomous research controller contract."""

from research_lab.autonomous_research_controller_contract import (
    ALWAYS_FORBIDDEN,
    CONTROLLER_CONTRACT_VERSION,
    controller_contract,
    validate_controller_contract,
)


def main():
    assert CONTROLLER_CONTRACT_VERSION == "0.1"
    assert validate_controller_contract() is True

    proceed = controller_contract("proceed")
    assert proceed["may_prepare_research_change"] is True
    assert proceed["may_prepare_repair"] is False
    assert proceed["external_action_authorized"] is False

    repair = controller_contract("repair")
    assert repair["may_prepare_repair"] is True
    assert repair["may_prepare_research_change"] is False

    wait = controller_contract("wait")
    assert wait["must_wait"] is True

    stop = controller_contract("stop")
    assert stop["must_stop"] is True

    required_forbidden = {
        "modify_main_branch",
        "execute_supabase_ddl",
        "change_secrets_or_credentials",
        "change_billing_or_paid_plan",
        "purchase_real_item",
        "sell_real_item",
        "execute_payment",
    }
    assert required_forbidden.issubset(set(ALWAYS_FORBIDDEN))

    try:
        controller_contract("unknown")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")

    print("Autonomous research controller contract tests passed")


if __name__ == "__main__":
    main()
