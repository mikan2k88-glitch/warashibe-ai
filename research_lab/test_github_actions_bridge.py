"""Tests for the GitHub Actions dashboard bridge."""

from research_lab.github_actions_bridge import live_snapshot


def run():
    # Network availability is intentionally not required by CI.
    snap = live_snapshot("test_stage", "test_next", 16)
    if snap is not None:
        assert snap["source"] == "github_actions"
        assert snap["total_checks"] == 16
        assert 0 <= snap["check_percent"] <= 100


if __name__ == "__main__":
    run()
    print("GITHUB ACTIONS BRIDGE: PASSED")
