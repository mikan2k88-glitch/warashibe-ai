"""Contract for one scheduled GPT Supervisor runtime invocation.

The contract defines what a scheduled supervisor run may inspect, how many
bounded development cycles it may attempt, what it may delegate to Gemini and
Codex, and when it must stop. It performs no live scheduling or API calls.
"""

SCHEDULED_SUPERVISOR_RUNTIME_CONTRACT_VERSION = "0.1"

DEFAULT_MAX_CYCLES = 3
DEFAULT_MAX_REPAIRS_PER_CYCLE = 1

REQUIRED_RUNTIME_INPUTS = (
    "run_id",
    "triggered_at",
    "milestone_id",
    "current_stage",
    "next_theme",
    "latest_ci_green",
    "human_gate_pending",
)

STOP_CONDITIONS = (
    "human_gate_required",
    "latest_ci_not_green",
    "policy_violation",
    "unknown_capability",
    "repair_budget_exhausted",
    "cycle_budget_exhausted",
    "milestone_complete",
)

ALLOWED_DELEGATIONS = (
    "gpt_to_gemini_assignment",
    "gemini_to_codex_task_draft",
    "codex_bounded_code_task",
)


def build_scheduled_runtime_contract(
    run_id,
    triggered_at,
    milestone_id,
    current_stage,
    next_theme,
    latest_ci_green,
    human_gate_pending,
    max_cycles=DEFAULT_MAX_CYCLES,
):
    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_CONTRACT_VERSION,
        "run_id": run_id,
        "triggered_at": triggered_at,
        "milestone_id": milestone_id,
        "current_stage": current_stage,
        "next_theme": next_theme,
        "latest_ci_green": bool(latest_ci_green),
        "human_gate_pending": bool(human_gate_pending),
        "max_cycles": max_cycles,
        "max_repairs_per_cycle": DEFAULT_MAX_REPAIRS_PER_CYCLE,
        "allowed_delegations": ALLOWED_DELEGATIONS,
        "stop_conditions": STOP_CONDITIONS,
        "may_inspect_repository": True,
        "may_inspect_ci": True,
        "may_select_next_theme": True,
        "may_assign_gemini": True,
        "may_prepare_codex_task": True,
        "may_run_offline_tests": True,
        "may_prepare_research_lab_commit": True,
        "may_write_main_without_human_gate": False,
        "may_read_or_write_secrets": False,
        "may_modify_production_config": False,
        "may_execute_commerce": False,
        "may_activate_live_external_api": False,
        "live_scheduler_connected": False,
        "live_gemini_connected": False,
        "live_codex_connected": False,
        "runtime_execution_authorized": False,
        "external_action_authorized": False,
    }


def validate_scheduled_runtime_contract(contract):
    if not isinstance(contract, dict):
        return {
            "valid": False,
            "errors": ("contract_not_mapping",),
            "runtime_execution_authorized": False,
        }

    errors = []

    for field in REQUIRED_RUNTIME_INPUTS:
        if field not in contract:
            errors.append(f"missing_{field}")

    if contract.get("version") != SCHEDULED_SUPERVISOR_RUNTIME_CONTRACT_VERSION:
        errors.append("unsupported_version")

    run_id = contract.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("invalid_run_id")

    milestone_id = contract.get("milestone_id")
    if not isinstance(milestone_id, str) or not milestone_id.strip():
        errors.append("invalid_milestone_id")

    current_stage = contract.get("current_stage")
    if not isinstance(current_stage, str) or not current_stage.strip():
        errors.append("invalid_current_stage")

    next_theme = contract.get("next_theme")
    if not isinstance(next_theme, str) or not next_theme.strip():
        errors.append("invalid_next_theme")

    max_cycles = contract.get("max_cycles")
    if not isinstance(max_cycles, int) or isinstance(max_cycles, bool):
        errors.append("invalid_max_cycles")
    elif not 1 <= max_cycles <= 10:
        errors.append("max_cycles_out_of_range")

    if contract.get("max_repairs_per_cycle") != 1:
        errors.append("invalid_repair_budget")

    if tuple(contract.get("stop_conditions") or ()) != STOP_CONDITIONS:
        errors.append("invalid_stop_conditions")

    if tuple(contract.get("allowed_delegations") or ()) != ALLOWED_DELEGATIONS:
        errors.append("invalid_allowed_delegations")

    for forbidden in (
        "may_write_main_without_human_gate",
        "may_read_or_write_secrets",
        "may_modify_production_config",
        "may_execute_commerce",
        "may_activate_live_external_api",
        "runtime_execution_authorized",
        "external_action_authorized",
    ):
        if contract.get(forbidden) is not False:
            errors.append(f"{forbidden}_must_be_false")

    return {
        "valid": not errors,
        "errors": tuple(dict.fromkeys(errors)),
        "runtime_execution_authorized": False,
        "external_action_authorized": False,
    }


def decide_scheduled_runtime_start(contract):
    validation = validate_scheduled_runtime_contract(contract)

    if not validation["valid"]:
        return {
            "start": False,
            "reason": "invalid_runtime_contract",
            "validation": validation,
        }

    if contract["human_gate_pending"] is True:
        return {
            "start": False,
            "reason": "human_gate_pending",
            "validation": validation,
        }

    if contract["latest_ci_green"] is not True:
        return {
            "start": False,
            "reason": "latest_ci_not_green",
            "validation": validation,
        }

    return {
        "start": False,
        "reason": "design_ready_but_live_runtime_not_activated",
        "validation": validation,
        "would_be_eligible_after_activation": True,
    }


def build_scheduled_supervisor_runtime_contract_design():
    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_CONTRACT_VERSION,
        "mode": "design_only",
        "default_max_cycles": DEFAULT_MAX_CYCLES,
        "max_repairs_per_cycle": DEFAULT_MAX_REPAIRS_PER_CYCLE,
        "stop_conditions": STOP_CONDITIONS,
        "allowed_delegations": ALLOWED_DELEGATIONS,
        "human_gate_blocks_start": True,
        "ci_green_required_at_start": True,
        "main_write_requires_human_gate": True,
        "scheduled_runtime_active": False,
        "runtime_execution_authorized": False,
        "external_action_authorized": False,
    }


def validate_scheduled_supervisor_runtime_contract_design():
    design = build_scheduled_supervisor_runtime_contract_design()
    assert design["mode"] == "design_only"
    assert design["default_max_cycles"] == 3
    assert design["max_repairs_per_cycle"] == 1
    assert design["human_gate_blocks_start"] is True
    assert design["ci_green_required_at_start"] is True
    assert design["main_write_requires_human_gate"] is True
    assert design["scheduled_runtime_active"] is False
    assert design["runtime_execution_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
