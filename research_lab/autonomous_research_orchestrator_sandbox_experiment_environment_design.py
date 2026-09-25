"""Design an isolated, disposable experiment environment for Warashibe AI.

The sandbox is a design-only contract. It does not create containers, install
packages, access secrets, enable networking, or execute external systems.
"""

SANDBOX_EXPERIMENT_ENVIRONMENT_DESIGN_VERSION = "0.1"

DEFAULT_ALLOWED_PURPOSES = (
    "module_scout_experiment",
    "codex_generated_code_test",
    "dependency_compatibility_test",
    "performance_micro_benchmark",
    "real_world_market_adapter_dry_run",
)

DEFAULT_RESOURCE_LIMITS = {
    "cpu_seconds": 60,
    "memory_mb": 512,
    "wall_time_seconds": 120,
    "disk_mb": 256,
}

DEFAULT_FILESYSTEM_POLICY = {
    "mode": "ephemeral",
    "project_mount": "read_only",
    "scratch_space": "write_only_ephemeral",
    "persist_artifacts": False,
}

DEFAULT_NETWORK_POLICY = {
    "enabled": False,
    "allowlist": (),
}

DEFAULT_SECRET_POLICY = {
    "inject_secrets": False,
    "inherit_environment": False,
    "allow_render_environment": False,
}


def build_sandbox_experiment_environment_design():
    return {
        "version": SANDBOX_EXPERIMENT_ENVIRONMENT_DESIGN_VERSION,
        "mode": "design_only",
        "lifecycle": "create_run_collect_destroy",
        "disposable": True,
        "allowed_purposes": DEFAULT_ALLOWED_PURPOSES,
        "resource_limits": dict(DEFAULT_RESOURCE_LIMITS),
        "filesystem_policy": dict(DEFAULT_FILESYSTEM_POLICY),
        "network_policy": dict(DEFAULT_NETWORK_POLICY),
        "secret_policy": dict(DEFAULT_SECRET_POLICY),
        "research_lab_only": True,
        "requires_reversible_experiment": True,
        "requires_test_or_ci_comparison": True,
        "auto_install_dependencies": False,
        "auto_network_enable": False,
        "auto_persist_state": False,
        "main_branch_authorized": False,
        "production_change_authorized": False,
        "credentials_change_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
        "execution_authorized": False,
        "human_gate_required_for_network_or_secrets": True,
        "experiment_flow": (
            "validate_request",
            "create_ephemeral_environment",
            "mount_project_read_only",
            "run_bounded_experiment",
            "collect_non_secret_results",
            "compare_tests_and_metrics",
            "destroy_environment",
            "adopt_or_reject",
        ),
    }


def validate_sandbox_experiment_environment_design():
    design = build_sandbox_experiment_environment_design()
    assert design["mode"] == "design_only"
    assert design["lifecycle"] == "create_run_collect_destroy"
    assert design["disposable"] is True
    assert design["research_lab_only"] is True
    assert design["filesystem_policy"]["project_mount"] == "read_only"
    assert design["filesystem_policy"]["scratch_space"] == "write_only_ephemeral"
    assert design["filesystem_policy"]["persist_artifacts"] is False
    assert design["network_policy"]["enabled"] is False
    assert design["network_policy"]["allowlist"] == ()
    assert design["secret_policy"]["inject_secrets"] is False
    assert design["secret_policy"]["inherit_environment"] is False
    assert design["secret_policy"]["allow_render_environment"] is False
    assert design["requires_reversible_experiment"] is True
    assert design["requires_test_or_ci_comparison"] is True
    assert design["auto_install_dependencies"] is False
    assert design["auto_network_enable"] is False
    assert design["auto_persist_state"] is False
    assert design["main_branch_authorized"] is False
    assert design["production_change_authorized"] is False
    assert design["credentials_change_authorized"] is False
    assert design["commerce_authorized"] is False
    assert design["external_action_authorized"] is False
    assert design["execution_authorized"] is False
    assert design["human_gate_required_for_network_or_secrets"] is True
    return True
