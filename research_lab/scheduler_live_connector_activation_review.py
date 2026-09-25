"""Read-only readiness review for the scheduler connector."""

from research_lab.scheduler_live_connector_implementation_design import validate_scheduler_trigger


def review_scheduler_activation(trigger, ci_green=False, connector_verified=False,
                                healthcheck_passed=False, human_gate=True):
    blockers = []
    if not validate_scheduler_trigger(trigger)["valid"]:
        blockers.append("invalid_trigger")
    if ci_green is not True:
        blockers.append("latest_ci_not_green")
    if connector_verified is not True:
        blockers.append("connector_not_verified")
    if healthcheck_passed is not True:
        blockers.append("healthcheck_not_passed")
    if human_gate is not False:
        blockers.append("human_gate_active")
    return {"mode": "review_only", "ready_for_activation_gate": not blockers,
            "blockers": tuple(blockers), "activation_authorized": False,
            "external_action_authorized": False}
