from research_lab.sandbox_execution_preflight import assess_sandbox_runtime


def main():
    default = assess_sandbox_runtime()
    assert default["status"] == "blocked"
    assert default["executor_invoked"] is False
    assert "design_execution_authorized" in default["blockers"]

    nominal = assess_sandbox_runtime(
        ci_status="success", human_gate_approved=True,
        runtime_verified=True, isolation_verified=True
    )
    assert nominal["status"] == "blocked"
    assert nominal["blockers"] == ["design_execution_authorized"]
    assert nominal["main_branch_authorized"] is False

    wrong_branch = assess_sandbox_runtime(
        branch="main", ci_status="success", human_gate_approved=True,
        runtime_verified=True, isolation_verified=True
    )
    assert "research_branch" in wrong_branch["blockers"]
    print("Sandbox execution preflight: PASS (fail-closed)")


if __name__ == "__main__":
    main()
