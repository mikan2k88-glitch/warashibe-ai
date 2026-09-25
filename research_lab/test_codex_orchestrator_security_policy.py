"""Tests for centralized Codex Orchestrator security policy."""

from research_lab.codex_orchestrator_security_policy import (
    build_orchestrator_security_policy,
    validate_codex_orchestrator_security_policy,
    validate_orchestrator_code_task,
)


def run_tests():
    assert validate_codex_orchestrator_security_policy() is True

    research_task = {
        "branch": "research-lab",
        "orchestrator_authorized": True,
        "requested_capabilities": (
            "inspect_repository",
            "edit_code_files",
            "run_offline_tests",
        ),
    }
    research = validate_orchestrator_code_task(research_task)
    assert research["valid"] is True
    assert research["code_write_scope"] == "all_repository_code"

    main_task = {
        "branch": "main",
        "orchestrator_authorized": True,
        "requested_capabilities": (
            "modify_main_branch_code",
            "edit_code_files",
            "run_offline_tests",
        ),
    }
    main = validate_orchestrator_code_task(main_task)
    assert main["valid"] is False
    assert "human_gate_required_for_main_write" in main["errors"]

    approved_main = validate_orchestrator_code_task(
        dict(main_task, human_gate_approved=True)
    )
    assert approved_main["valid"] is True

    generic_main = validate_orchestrator_code_task(
        dict(main_task, requested_capabilities=("edit_code_files",))
    )
    assert "human_gate_required_for_main_write" in generic_main["errors"]

    mislabeled_main = validate_orchestrator_code_task(
        dict(research_task, requested_capabilities=("modify_main_branch_code",))
    )
    assert "human_gate_required_for_main_write" in mislabeled_main["errors"]

    main_read = validate_orchestrator_code_task(
        dict(main_task, requested_capabilities=("inspect_repository",))
    )
    assert main_read["valid"] is True

    no_orchestrator = dict(main_task, orchestrator_authorized=False)
    rejected = validate_orchestrator_code_task(no_orchestrator)
    assert rejected["valid"] is False
    assert "orchestrator_authorization_required" in rejected["errors"]

    sensitive = dict(
        main_task,
        requested_capabilities=("write_secrets",),
    )
    blocked_sensitive = validate_orchestrator_code_task(sensitive)
    assert blocked_sensitive["valid"] is False
    assert "human_gate_required_for_sensitive_action" in blocked_sensitive["errors"]

    sensitive_approved = dict(sensitive, human_gate_approved=True)
    accepted_sensitive = validate_orchestrator_code_task(sensitive_approved)
    assert accepted_sensitive["valid"] is True

    policy = build_orchestrator_security_policy()
    assert policy["main_code_changes_allowed"] is True
    assert policy["security_owner"] == "warashibe_orchestrator"
    assert policy["codex_self_escalation_allowed"] is False


if __name__ == "__main__":
    run_tests()
    print("Codex orchestrator security policy tests passed")
