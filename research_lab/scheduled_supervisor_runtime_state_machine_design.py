"""State machine for one scheduled GPT Supervisor runtime run.

The state machine unifies the scheduled supervisor lifecycle. It translates
bounded runtime events into explicit states without performing live scheduler,
Gemini, Codex, GitHub, or commerce actions.
"""

SCHEDULED_SUPERVISOR_RUNTIME_STATE_MACHINE_VERSION = "0.1"

STATES = (
    "idle",
    "running",
    "waiting_ci",
    "waiting_human",
    "repairing",
    "completed",
    "stopped",
)

EVENTS = (
    "start",
    "cycle_dispatched",
    "ci_pending",
    "ci_green",
    "ci_failed",
    "human_gate_required",
    "repair_available",
    "repair_exhausted",
    "milestone_complete",
    "cycle_budget_exhausted",
    "policy_violation",
    "unknown_capability",
    "reset",
)

TERMINAL_STATES = (
    "completed",
    "stopped",
)


def build_runtime_state(
    run_id,
    state="idle",
    current_cycle=0,
    repairs_used=0,
    max_cycles=3,
):
    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_STATE_MACHINE_VERSION,
        "run_id": run_id,
        "state": state,
        "current_cycle": current_cycle,
        "repairs_used": repairs_used,
        "max_cycles": max_cycles,
        "max_repairs_per_cycle": 1,
        "runtime_execution_authorized": False,
        "external_action_authorized": False,
    }


def validate_runtime_state(runtime):
    if not isinstance(runtime, dict):
        return {"valid": False, "errors": ("runtime_not_mapping",)}

    errors = []

    run_id = runtime.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("invalid_run_id")

    if runtime.get("state") not in STATES:
        errors.append("invalid_state")

    current_cycle = runtime.get("current_cycle")
    if not isinstance(current_cycle, int) or isinstance(current_cycle, bool):
        errors.append("invalid_current_cycle")
    elif current_cycle < 0:
        errors.append("current_cycle_out_of_range")

    repairs_used = runtime.get("repairs_used")
    if not isinstance(repairs_used, int) or isinstance(repairs_used, bool):
        errors.append("invalid_repairs_used")
    elif repairs_used < 0:
        errors.append("repairs_used_out_of_range")

    max_cycles = runtime.get("max_cycles")
    if not isinstance(max_cycles, int) or isinstance(max_cycles, bool):
        errors.append("invalid_max_cycles")
    elif not 1 <= max_cycles <= 10:
        errors.append("max_cycles_out_of_range")

    if runtime.get("max_repairs_per_cycle") != 1:
        errors.append("invalid_max_repairs_per_cycle")

    return {
        "valid": not errors,
        "errors": tuple(dict.fromkeys(errors)),
    }


def transition_runtime_state(runtime, event):
    validation = validate_runtime_state(runtime)
    if not validation["valid"]:
        return {
            "transitioned": False,
            "state": "stopped",
            "reason": "invalid_runtime_state",
            "validation": validation,
        }

    if event not in EVENTS:
        return {
            "transitioned": False,
            "state": "stopped",
            "reason": "unknown_event",
            "validation": validation,
        }

    current = runtime["state"]

    if event == "reset":
        return {
            "transitioned": True,
            "state": "idle",
            "current_cycle": 0,
            "repairs_used": 0,
            "reason": "runtime_reset",
        }

    if current in TERMINAL_STATES:
        return {
            "transitioned": False,
            "state": current,
            "reason": "terminal_state_requires_reset",
        }

    if event in ("policy_violation", "unknown_capability", "repair_exhausted"):
        return {
            "transitioned": True,
            "state": "stopped",
            "reason": event,
        }

    if event in ("milestone_complete", "cycle_budget_exhausted"):
        return {
            "transitioned": True,
            "state": "completed",
            "reason": event,
        }

    if event == "human_gate_required":
        return {
            "transitioned": True,
            "state": "waiting_human",
            "reason": "human_gate_required",
        }

    if current == "idle" and event == "start":
        return {
            "transitioned": True,
            "state": "running",
            "current_cycle": runtime["current_cycle"],
            "repairs_used": runtime["repairs_used"],
            "reason": "runtime_started",
        }

    if current == "running" and event in ("cycle_dispatched", "ci_pending"):
        return {
            "transitioned": True,
            "state": "waiting_ci",
            "reason": "awaiting_ci_result",
        }

    if current == "waiting_ci" and event == "ci_green":
        next_cycle = runtime["current_cycle"] + 1
        if next_cycle >= runtime["max_cycles"]:
            return {
                "transitioned": True,
                "state": "completed",
                "current_cycle": next_cycle,
                "repairs_used": 0,
                "reason": "cycle_budget_exhausted",
            }
        return {
            "transitioned": True,
            "state": "running",
            "current_cycle": next_cycle,
            "repairs_used": 0,
            "reason": "ci_green_advance_cycle",
        }

    if current == "waiting_ci" and event in ("ci_failed", "repair_available"):
        if runtime["repairs_used"] < runtime["max_repairs_per_cycle"]:
            return {
                "transitioned": True,
                "state": "repairing",
                "current_cycle": runtime["current_cycle"],
                "repairs_used": runtime["repairs_used"] + 1,
                "reason": "single_repair_authorized",
            }
        return {
            "transitioned": True,
            "state": "stopped",
            "reason": "repair_budget_exhausted",
        }

    if current == "repairing" and event in ("cycle_dispatched", "ci_pending"):
        return {
            "transitioned": True,
            "state": "waiting_ci",
            "reason": "repair_waiting_ci",
        }

    if current == "waiting_human":
        return {
            "transitioned": False,
            "state": "waiting_human",
            "reason": "human_gate_resolution_required",
        }

    return {
        "transitioned": False,
        "state": current,
        "reason": "event_not_allowed_from_current_state",
    }


def build_state_machine_design():
    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_STATE_MACHINE_VERSION,
        "mode": "design_only",
        "states": STATES,
        "events": EVENTS,
        "terminal_states": TERMINAL_STATES,
        "default_initial_state": "idle",
        "max_repairs_per_cycle": 1,
        "human_gate_state": "waiting_human",
        "ci_wait_state": "waiting_ci",
        "repair_state": "repairing",
        "runtime_execution_authorized": False,
        "external_action_authorized": False,
    }


def validate_scheduled_supervisor_runtime_state_machine_design():
    design = build_state_machine_design()
    assert design["mode"] == "design_only"
    assert design["default_initial_state"] == "idle"
    assert design["max_repairs_per_cycle"] == 1
    assert design["human_gate_state"] == "waiting_human"
    assert design["ci_wait_state"] == "waiting_ci"
    assert design["repair_state"] == "repairing"
    assert design["runtime_execution_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
