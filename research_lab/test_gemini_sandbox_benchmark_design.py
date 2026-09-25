"""Tests for Gemini sandbox benchmark design."""

from research_lab.gemini_sandbox_benchmark_design import (
    build_gemini_sandbox_benchmark_design,
    validate_gemini_sandbox_benchmark_design,
)


def run_tests():
    assert validate_gemini_sandbox_benchmark_design() is True

    design = build_gemini_sandbox_benchmark_design()
    assert design["models"] == (
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.5-flash",
    )
    assert "structured_json_candidate_evaluation" in design["tasks"]
    assert "stop_loss_decision" in design["tasks"]
    assert "schema_valid_rate" in design["metrics"]
    assert "estimated_cost" in design["metrics"]
    assert design["repeat_count_per_case"] == 5
    assert design["requires_deterministic_fixtures"] is True
    assert design["requires_failure_injection"] is True
    assert design["network_execution_authorized"] is False
    assert design["secret_access_authorized"] is False
    assert design["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("gemini sandbox benchmark design tests passed")
