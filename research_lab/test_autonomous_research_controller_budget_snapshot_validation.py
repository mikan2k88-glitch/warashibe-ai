"""Tests for controller budget snapshot validation."""

from research_lab.autonomous_research_controller_budget_snapshot import (
    controller_budget_snapshot,
)
from research_lab.autonomous_research_controller_budget_snapshot_validation import (
    validate_budget_snapshot,
    validate_controller_budget_snapshot_validation,
)


def run_tests():
    assert validate_controller_budget_snapshot_validation() is True

    snapshot = controller_budget_snapshot("repair", "prepare_repair")
    result = validate_budget_snapshot(snapshot)
    assert result["valid"] is True
    assert result["external_action_performed"] is False

    missing = dict(snapshot)
    del missing["usage"]
    result = validate_budget_snapshot(missing)
    assert result["valid"] is False
    assert result["reason"] == "missing_fields"
    assert result["missing"] == ("usage",)

    assert validate_budget_snapshot(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("controller budget snapshot validation tests passed")
