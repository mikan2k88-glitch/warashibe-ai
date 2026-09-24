"""Pure state machine for the future autonomous research orchestrator.

It decides the next control state only. It performs no GitHub, database,
deployment, credential, billing, or real-world action.
"""

from research_lab.autonomous_research_orchestrator_design import classify_action

STATE_MACHINE_VERSION = "0.1"

STATES = (
    "inspect",
    "work",
    "verify_ci",
    "repair",
    "human_gate",
    "stopped",
)


def next_state(state, *, action=None, ci_status=None, repairable=True):
    if state == "inspect":
        classification = classify_action(action)
        if classification == "autonomous":
            return "work"
        if classification == "human_gate":
            return "human_gate"
        return "stopped"

    if state == "work":
        return "verify_ci"

    if state == "verify_ci":
        if ci_status == "success":
            return "inspect"
        if ci_status == "failure" and repairable:
            return "repair"
        if ci_status == "failure":
            return "stopped"
        return "verify_ci"

    if state == "repair":
        return "verify_ci"

    if state in ("human_gate", "stopped"):
        return state

    return "stopped"


def validate_state_machine():
    assert next_state("inspect", action="edit_research_lab_code") == "work"
    assert next_state("inspect", action="execute_supabase_ddl") == "human_gate"
    assert next_state("inspect", action="unknown") == "stopped"
    assert next_state("work") == "verify_ci"
    assert next_state("verify_ci", ci_status="success") == "inspect"
    assert next_state("verify_ci", ci_status="failure", repairable=True) == "repair"
    assert next_state("verify_ci", ci_status="failure", repairable=False) == "stopped"
    assert next_state("repair") == "verify_ci"
    assert next_state("human_gate") == "human_gate"
    assert next_state("stopped") == "stopped"
    return True
