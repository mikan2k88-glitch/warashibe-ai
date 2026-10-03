"""Runtime status snapshot contract tests."""

from research_lab.runtime_status import build_runtime_status_snapshot


def main():
    snapshot = build_runtime_status_snapshot(
        service_name="warashibe-ai-research-lab",
        service_id="srv-daq2dru7bikc73bb9ik0",
        branch="research-lab",
        git_head_sha="ec4a965036fc3d7462dc702c313e732c5c493782",
        ci_sha="ec4a965036fc3d7462dc702c313e732c5c493782",
        ci_status="success",
        render_live_sha="ec4a965036fc3d7462dc702c313e732c5c493782",
        render_deploy_id="dep-db0bdfajtthc73f28um0",
        render_status="live",
        observed_at="2026-10-03T08:30:00+00:00",
        source="render_connector",
    )

    assert snapshot["status"] == "runtime_status_verified"
    assert snapshot["deployment_consistent"] is True
    assert snapshot["firecrawl_required"] is False
    assert snapshot["source_priority"] == [
        "supabase",
        "render_connector",
        "firecrawl",
    ]

    mismatch = build_runtime_status_snapshot(
        service_name="warashibe-ai-research-lab",
        service_id="srv-daq2dru7bikc73bb9ik0",
        branch="research-lab",
        git_head_sha="a",
        ci_sha="a",
        ci_status="success",
        render_live_sha="b",
        render_deploy_id="dep-x",
        render_status="live",
        observed_at="2026-10-03T08:31:00+00:00",
        source="render_connector",
    )
    assert mismatch["deployment_consistent"] is False
    assert mismatch["status"] == "runtime_status_inconsistent"
    assert mismatch["firecrawl_required"] is True

    print("Runtime status snapshot contract tests passed")


if __name__ == "__main__":
    main()
