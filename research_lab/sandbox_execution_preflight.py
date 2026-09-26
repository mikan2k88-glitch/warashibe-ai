"""Fail-closed bridge from Sandbox v0.1 design to a future runtime.

This module never launches containers, subprocesses, network calls or writes.
A design-only contract cannot authorize execution by itself.
"""
from research_lab.autonomous_research_orchestrator_sandbox_experiment_environment_design import (
    build_sandbox_experiment_environment_design,
)


def assess_sandbox_runtime(*, branch="research-lab", ci_status="unknown",
                           human_gate_approved=False, runtime_verified=False,
                           isolation_verified=False):
    design = build_sandbox_experiment_environment_design()
    checks = {
        "research_branch": branch == "research-lab",
        "ci_green": ci_status == "success",
        "human_gate": human_gate_approved is True,
        "runtime_verified": runtime_verified is True,
        "isolation_verified": isolation_verified is True,
        "design_execution_authorized": design["execution_authorized"] is True,
        "network_disabled": design["network_policy"]["enabled"] is False,
        "secrets_disabled": design["secret_policy"]["inherit_environment"] is False
                            and design["secret_policy"]["inject_secrets"] is False,
        "read_only_project": design["filesystem_policy"]["project_mount"] == "read_only",
        "ephemeral_scratch": design["filesystem_policy"]["persist_artifacts"] is False,
        "limits_present": all(isinstance(value, int) and value > 0
                              for value in design["resource_limits"].values()),
    }
    blockers = [name for name, passed in checks.items() if not passed]
    return {
        "mode": "preflight_only",
        "status": "blocked" if blockers else "ready_for_separate_runtime_review",
        "checks": checks,
        "blockers": blockers,
        "executor_invoked": False,
        "main_branch_authorized": False,
        "external_action_authorized": False,
    }
