"""Design a continuous rational-improvement loop for Warashibe AI.

The loop reviews completed system work for small, reversible improvements and
explicitly considers reuse of standard libraries, mature OSS, official APIs,
and plugin-style modules before proposing more custom code.
"""

KAIZEN_LOOP_DESIGN_VERSION = "0.1"

DEFAULT_REVIEW_DIMENSIONS = (
    "duplication",
    "layer_count",
    "complexity",
    "test_time",
    "ci_time",
    "failure_rate",
    "safety_boundary_redundancy",
    "reusability",
    "maintainability",
    "performance",
)

DEFAULT_REUSE_ORDER = (
    "python_standard_library",
    "official_project_api_or_sdk",
    "mature_open_source_module",
    "internal_shared_module",
    "custom_implementation",
)

DEFAULT_MODULE_REVIEW_CRITERIA = (
    "maintenance_activity",
    "license_compatibility",
    "security_posture",
    "dependency_weight",
    "python_compatibility",
    "testability",
    "rollback_cost",
    "custom_code_reduction",
)


def build_kaizen_loop_design():
    return {
        "version": KAIZEN_LOOP_DESIGN_VERSION,
        "mode": "review_then_experiment",
        "review_dimensions": DEFAULT_REVIEW_DIMENSIONS,
        "reuse_order": DEFAULT_REUSE_ORDER,
        "module_review_criteria": DEFAULT_MODULE_REVIEW_CRITERIA,
        "module_scout_enabled": True,
        "prefer_reuse_before_build": True,
        "requires_small_reversible_experiment": True,
        "requires_ci_comparison": True,
        "auto_large_refactor": False,
        "auto_external_install": False,
        "auto_dependency_upgrade": False,
        "auto_network_execution": False,
        "main_branch_authorized": False,
        "production_change_authorized": False,
        "credentials_change_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
        "improvement_flow": (
            "review_existing_system",
            "identify_candidate",
            "check_reuse_options",
            "rank_small_reversible_experiment",
            "run_research_lab_experiment",
            "compare_ci_and_quality",
            "adopt_or_revert",
            "standardize_if_adopted",
        ),
    }


def validate_kaizen_loop_design():
    design = build_kaizen_loop_design()
    assert design["mode"] == "review_then_experiment"
    assert design["module_scout_enabled"] is True
    assert design["prefer_reuse_before_build"] is True
    assert design["reuse_order"][0] == "python_standard_library"
    assert design["reuse_order"][-1] == "custom_implementation"
    assert "license_compatibility" in design["module_review_criteria"]
    assert "security_posture" in design["module_review_criteria"]
    assert design["requires_small_reversible_experiment"] is True
    assert design["requires_ci_comparison"] is True
    assert design["auto_large_refactor"] is False
    assert design["auto_external_install"] is False
    assert design["auto_dependency_upgrade"] is False
    assert design["auto_network_execution"] is False
    assert design["main_branch_authorized"] is False
    assert design["production_change_authorized"] is False
    assert design["credentials_change_authorized"] is False
    assert design["commerce_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
