"""Tests for live runtime connector implementation review."""

from research_lab.live_runtime_connector_implementation_review import (
    build_connector_implementation_review,
    build_live_runtime_connector_implementation_review_design,
    validate_live_runtime_connector_implementation_review,
    validate_live_runtime_connector_implementation_review_design,
)


def run_tests():
    assert validate_live_runtime_connector_implementation_review_design() is True

    review = build_connector_implementation_review(
        scheduler_ready=True,
        gemini_ready=True,
        codex_ready=False,
    )
    validation = validate_live_runtime_connector_implementation_review(review)
    assert validation["valid"] is True
    assert review["next_connector"] == "scheduler"
    assert review["scheduler_can_be_implemented_first"] is True
    assert review["gemini_live_call_requires_separate_activation_gate"] is True
    assert review["codex_live_call_requires_callable_runtime"] is True
    assert "codex_callable_runtime_not_available" in review["blockers"]
    assert review["live_implementation_authorized"] is False
    assert review["secret_access_authorized"] is False
    assert review["external_action_authorized"] is False

    blocked_scheduler = build_connector_implementation_review(
        scheduler_ready=False,
        gemini_ready=True,
        codex_ready=False,
    )
    blocked_validation = validate_live_runtime_connector_implementation_review(
        blocked_scheduler
    )
    assert blocked_validation["valid"] is True
    assert blocked_scheduler["next_connector"] == "gemini"
    assert "scheduler_design_not_ready" in blocked_scheduler["blockers"]

    design = build_live_runtime_connector_implementation_review_design()
    assert design["scheduler_first"] is True
    assert design["codex_after_callable_runtime_exists"] is True
    assert design["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Live runtime connector implementation review tests passed")
