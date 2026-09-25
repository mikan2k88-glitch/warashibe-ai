"""Cycle controller for one scheduled GPT Supervisor runtime run.

Tracks bounded autonomous cycles, CI gating, repair budget, milestone completion,
and HUMAN GATE stops. This module performs no live scheduler, Gemini, Codex,
GitHub, or commerce action.
"""

SCHEDULED_SUPERVISOR_RUNTIME_CYCLE_CONTROLLER_VERSION = "0.1"

CYCLE_ACTIONS = (
    "start_cycle",
    "await_ci",
    "repair_once",
    "advance_cycle",
    "stop",
    "request_human_gate",
    "complete_run",
)

STOP_REASONS = (
    "human_gate_required",
    "policy_violation",
    "unknown_capability",
    "repair_budget_exhausted",
    "cycle_budget_exhausted",
    "milestone_complete",
    "ci_not_green",
)


def build_cycle_state(
    run_id,
    max_cycles=3,
    current_cycle=0,
    repairs_used=0,
    latest_ci_green=True,
    human_gate_pending=False,
    milestone_complete=False,
    policy_violation=False,
    unknown_capability=False,
):
    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_CYCLE_CONTROLLER_VERSION,
        "run_id": run_id,
        "max_cycles": max_cycles,
        "current_cycle": current_cycle,
        "repairs_used": repairs_used,
        "max_repairs_per_cycle": 1,
        "latest_ci_green": bool(latest_ci_green),
        "human_gate_pending": bool(human_gate_pending),
        "milestone_complete": bool(milestone_complete),
        "policy_violation": bool(policy_violation),
        "unknown_capability": bool(unknown_capability),
        "runtime_execution_authorized": False,
        "external_action_authorized": False,
    }


def validate_cycle_state(state):
    if not isinstance(state, dict):
        return {
            "valid": False,
            "errors": ("state_not_mapping",),
        }

    errors = []

    run_id = state.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("invalid_run_id")

    max_cycles = state.get("max_cycles")
    if not isinstance(max_cycles, int) or isinstance(max_cycles, bool):
        errors.append("invalid_max_cycles")
    elif not 1 <= max_cycles <= 10:
        errors.append("max_cycles_out_of_range")

    current_cycle = state.get("current_cycle")
    if not isinstance(current_cycle, int) or isinstance(current_cycle, bool):
        errors.append("invalid_current_cycle")
    elif current_cycle < 0:
        errors.append("current_cycle_out_of_range")

    repairs_used = state.get("repairs_used")
    if not isinstance(repairs_used, int) or isinstance(repairs_used, bool):
        errors.append("invalid_repairs_used")
    elif repairs_used < 0:
        errors.append("repairs_used_out_of_range")

    if state.get("max_repairs_per_cycle") != 1:
        errors.append("invalid_max_repairs_per_cycle")

    for field in (
        "latest_ci_green",
        "human_gate_pending",
        "milestone_complete",
        "policy_violation",
        "unknown_capability",
    ):
        if not isinstance(state.get(field), bool):
            errors.append(f"invalid_{field}")

    return {
        "valid": not errors,
        "errors": tuple(dict.fromkeys(errors)),
        "runtime_execution_authorized": False,
        "external_action_authorized": False,
    }


def decide_cycle_action(state, last_cycle_status=None):
    validation = validate_cycle_state(state)
    if not validation["valid"]:
        return {
            "action": "stop",
            "reason": "invalid_cycle_state",
            "validation": validation,
        }

    if state["human_gate_pending"]:
        return {
            "action": "request_human_gate",
            "reason": "human_gate_required",
            "validation": validation,
        }

    if state["policy_violation"]:
        return {
            "action": "stop",
            "reason": "policy_violation",
            "validation": validation,
        }

    if state["unknown_capability"]:
        return {
            "action": "stop",
            "reason": "unknown_capability",
            "validation": validation,
        }

    if state["milestone_complete"]:
        return {
            "action": "complete_run",
            "reason": "milestone_complete",
            "validation": validation,
        }

    if state["current_cycle"] >= state["max_cycles"]:
        return {
            "action": "complete_run",
            "reason": "cycle_budget_exhausted",
            "validation": validation,
        }

    if last_cycle_status == "failed":
        if state["repairs_used"] < state["max_repairs_per_cycle"]:
            return {
                "action": "repair_once",
                "reason": "single_repair_available",
                "next_repairs_used": state["repairs_used"] + 1,
                "validation": validation,
            }
        return {
            "action": "stop",
            "reason": "repair_budget_exhausted",
            "validation": validation,
        }

    if last_cycle_status == "awaiting_ci":
        return {
            "action": "await_ci",
            "reason": "ci_result_pending",
            "validation": validation,
        }

    if last_cycle_status == "completed":
        if state["latest_ci_green"] is not True:
            return {
                "action": "stop",
                "reason": "ci_not_green",
                "validation": validation,
            }
        return {
            "action": "advance_cycle",
            "reason": "previous_cycle_green",
            "next_cycle": state["current_cycle"] + 1,
            "reset_repairs_used": 0,
            "validation": validation,
        }

    if state["latest_ci_green"] is not True:
        return {
            "action": "stop",
            "reason": "ci_not_green",
            "validation": validation,
        }

    return {
        "action": "start_cycle",
        "reason": "cycle_ready",
        "cycle_number": state["current_cycle"] + 1,
        "validation": validation,
    }


def build_cycle_controller_design():
    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_CYCLE_CONTROLLER_VERSION,
        "mode": "design_only",
        "actions": CYCLE_ACTIONS,
        "stop_reasons": STOP_REASONS,
        "default_max_cycles": 3,
        "max_repairs_per_cycle": 1,
        "ci_green_required_between_cycles": True,
        "human_gate_preempts_cycle": True,
        "policy_violation_stops_run": True,
        "unknown_capability_stops_run": True,
        "milestone_completion_stops_run": True,
        "runtime_execution_authorized": False,
        "external_action_authorized": False,
    }


def validate_scheduled_supervisor_runtime_cycle_controller_design():
    design = build_cycle_controller_design()
    assert design["mode"] == "design_only"
    assert design["default_max_cycles"] == 3
    assert design["max_repairs_per_cycle"] == 1
    assert design["ci_green_required_between_cycles"] is True
    assert design["human_gate_preempts_cycle"] is True
    assert design["policy_violation_stops_run"] is True
    assert design["unknown_capability_stops_run"] is True
    assert design["milestone_completion_stops_run"] is True
    assert design["runtime_execution_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
