"""Bridge controller decisions to the effective autonomous-research policy.

Pure planning helper: it authorizes no external action and performs none.
"""

from research_lab.autonomous_research_controller_contract import controller_contract
from research_lab.autonomous_research_policy_alignment import effective_limits

BRIDGE_VERSION = "0.1"


def controller_policy_bridge(decision):
    contract = controller_contract(decision)
    limits = effective_limits()
    return {
        "version": BRIDGE_VERSION,
        "decision": decision,
        "may_prepare_research_change": contract["may_prepare_research_change"],
        "may_prepare_repair": contract["may_prepare_repair"],
        "must_wait": contract["must_wait"],
        "must_stop": contract["must_stop"],
        "effective_limits": limits,
        "forbidden_actions": contract["forbidden_actions"],
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_controller_policy_bridge():
    proceed = controller_policy_bridge("proceed")
    assert proceed["may_prepare_research_change"] is True
    assert proceed["effective_limits"]["themes_per_cycle"] == 1
    assert proceed["effective_limits"]["repair_attempts_per_cycle"] == 1
    assert proceed["external_action_authorized"] is False
    for decision in ("repair", "wait", "stop"):
        bridged = controller_policy_bridge(decision)
        assert bridged["may_prepare_research_change"] is False
    return True
