"""Tests for GPT/Gemini/Codex control-plane design."""

from research_lab.gpt_gemini_codex_control_plane_design import (
    build_control_plane_design,
    validate_control_plane_design,
)


def run_tests():
    assert validate_control_plane_design() is True

    design = build_control_plane_design()

    assert design["roles"]["gpt_supervisor"]["role"] == "supervisor_scheduler"
    assert design["roles"]["gemini_orchestrator"]["role"] == "operations_orchestrator"
    assert design["roles"]["codex_worker"]["role"] == "implementation_worker"
    assert design["roles"]["safety_kernel_ci"]["role"] == "independent_control"

    assert design["roles"]["gpt_supervisor"]["may_directly_execute_commerce"] is False
    assert design["roles"]["gemini_orchestrator"]["may_self_authorize_sensitive_actions"] is False
    assert design["roles"]["codex_worker"]["may_self_authorize_policy_override"] is False
    assert design["roles"]["safety_kernel_ci"]["may_grant_human_authority"] is False

    assert "main_branch_write" in design["escalation_rules"]["gpt_to_human"]
    assert "milestone_boundary" in design["escalation_rules"]["gemini_to_gpt"]
    assert design["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("GPT Gemini Codex control plane design tests passed")
