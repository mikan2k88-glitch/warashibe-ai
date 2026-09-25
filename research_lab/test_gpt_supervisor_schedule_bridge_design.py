"""Tests for GPT supervisor schedule bridge design."""

from research_lab.gpt_supervisor_schedule_bridge_design import (
    build_gemini_assignment,
    build_gpt_supervisor_schedule_bridge_design,
    decide_supervisor_action,
    validate_gemini_assignment,
    validate_gpt_supervisor_schedule_bridge_design,
)


def _state():
    return {
        "schedule_tick_id": "tick-001",
        "milestone_id": "sandbox_external_integration",
        "current_stage": "codex_mcp_commit_controller_design",
        "next_theme": "gpt_supervisor_schedule_bridge_design",
        "latest_ci_green": True,
        "human_gate_pending": False,
        "milestone_complete": False,
    }


def run_tests():
    assert validate_gpt_supervisor_schedule_bridge_design() is True

    decision = decide_supervisor_action(_state())
    assert decision["valid"] is True
    assert decision["action"] == "assign_operational_goal"

    assignment_result = build_gemini_assignment(_state())
    assert assignment_result["created"] is True
    assignment = assignment_result["assignment"]
    assert assignment["milestone_id"] == "sandbox_external_integration"
    assert "gpt_supervisor_schedule_bridge_design" in assignment["goal"]
    assert assignment["gemini_execution_authorized"] is False
    assert assignment["codex_execution_authorized"] is False

    validation = validate_gemini_assignment(assignment)
    assert validation["valid"] is True
    assert validation["external_action_authorized"] is False

    ci_hold = _state()
    ci_hold["latest_ci_green"] = False
    held = decide_supervisor_action(ci_hold)
    assert held["action"] == "hold_for_ci"

    gate = _state()
    gate["human_gate_pending"] = True
    gated = decide_supervisor_action(gate)
    assert gated["action"] == "request_human_gate"

    complete = _state()
    complete["milestone_complete"] = True
    closed = decide_supervisor_action(complete)
    assert closed["action"] == "close_milestone"

    design = build_gpt_supervisor_schedule_bridge_design()
    assert design["supervisor"] == "gpt"
    assert design["operations_orchestrator"] == "gemini"
    assert design["implementation_worker"] == "codex"
    assert design["gemini_api_call_authorized"] is False
    assert design["codex_invocation_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("GPT supervisor schedule bridge design tests passed")
