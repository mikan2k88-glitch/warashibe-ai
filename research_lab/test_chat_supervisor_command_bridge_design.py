"""Tests for chat supervisor command bridge design."""

from research_lab.chat_supervisor_command_bridge_design import (
    build_chat_supervisor_command_bridge_design,
    build_supervisor_command,
    route_supervisor_command,
    validate_chat_supervisor_command_bridge_design,
    validate_supervisor_command,
)


def run_tests():
    assert validate_chat_supervisor_command_bridge_design() is True

    immediate = build_supervisor_command(
        command_id="chat-001",
        intent="Advance the next bounded development theme.",
        target_milestone="sandbox_external_integration",
        requested_scope=("research_lab",),
    )
    valid = validate_supervisor_command(immediate)
    assert valid["valid"] is True
    routed = route_supervisor_command(immediate)
    assert routed["status"] == "ready_for_supervisor_review"
    assert routed["next_action"] == "gpt_supervisor_review"

    scheduled = build_supervisor_command(
        command_id="chat-002",
        intent="Continue development while the user is away.",
        target_milestone="sandbox_external_integration",
        requested_scope=("research_lab",),
        delivery_mode="next_schedule_tick",
    )
    queued = route_supervisor_command(scheduled)
    assert queued["status"] == "queued_for_supervisor_tick"
    assert queued["next_action"] == "await_schedule_tick"

    gated = build_supervisor_command(
        command_id="chat-003",
        intent="Prepare a main branch write.",
        target_milestone="core_integration",
        requested_scope=("main",),
        human_gate_required=True,
    )
    gate_result = route_supervisor_command(gated)
    assert gate_result["status"] == "human_gate_required"
    assert gate_result["next_action"] == "request_human_gate"

    design = build_chat_supervisor_command_bridge_design()
    assert design["chat_is_command_ingress"] is True
    assert design["gpt_must_review_before_gemini"] is True
    assert design["supports_next_schedule_tick"] is True
    assert design["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Chat supervisor command bridge design tests passed")
