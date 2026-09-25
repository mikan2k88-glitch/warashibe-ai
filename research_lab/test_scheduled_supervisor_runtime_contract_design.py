"""Tests for scheduled GPT Supervisor runtime contract design."""

from research_lab.scheduled_supervisor_runtime_contract_design import (
    build_scheduled_runtime_contract,
    build_scheduled_supervisor_runtime_contract_design,
    decide_scheduled_runtime_start,
    validate_scheduled_runtime_contract,
    validate_scheduled_supervisor_runtime_contract_design,
)


def _contract(**overrides):
    data = {
        "run_id": "scheduled-run-001",
        "triggered_at": "2026-09-25T18:00:00+09:00",
        "milestone_id": "supervisory_closed_loop",
        "current_stage": "scheduled_supervisor_runtime_activation_review",
        "next_theme": "scheduled_supervisor_runtime_contract_design",
        "latest_ci_green": True,
        "human_gate_pending": False,
    }
    data.update(overrides)
    return build_scheduled_runtime_contract(**data)


def run_tests():
    assert validate_scheduled_supervisor_runtime_contract_design() is True

    contract = _contract()
    validation = validate_scheduled_runtime_contract(contract)
    assert validation["valid"] is True
    assert contract["max_cycles"] == 3
    assert contract["max_repairs_per_cycle"] == 1
    assert contract["may_write_main_without_human_gate"] is False
    assert contract["may_read_or_write_secrets"] is False
    assert contract["may_execute_commerce"] is False
    assert contract["runtime_execution_authorized"] is False

    start = decide_scheduled_runtime_start(contract)
    assert start["start"] is False
    assert start["reason"] == "design_ready_but_live_runtime_not_activated"
    assert start["would_be_eligible_after_activation"] is True

    ci_blocked = _contract(latest_ci_green=False)
    ci_decision = decide_scheduled_runtime_start(ci_blocked)
    assert ci_decision["start"] is False
    assert ci_decision["reason"] == "latest_ci_not_green"

    gate_blocked = _contract(human_gate_pending=True)
    gate_decision = decide_scheduled_runtime_start(gate_blocked)
    assert gate_decision["start"] is False
    assert gate_decision["reason"] == "human_gate_pending"

    too_many_cycles = _contract(max_cycles=11)
    invalid = validate_scheduled_runtime_contract(too_many_cycles)
    assert invalid["valid"] is False
    assert "max_cycles_out_of_range" in invalid["errors"]

    design = build_scheduled_supervisor_runtime_contract_design()
    assert design["default_max_cycles"] == 3
    assert design["max_repairs_per_cycle"] == 1
    assert design["scheduled_runtime_active"] is False
    assert design["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Scheduled supervisor runtime contract design tests passed")
