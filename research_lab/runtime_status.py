"""Verified runtime deployment status snapshots.

Supabase is the preferred read cache. Render remains the source of truth.
Firecrawl is only needed when the verified cache is absent/stale/inconsistent
and the Render connector cannot resolve the missing evidence.
"""

SOURCE_PRIORITY = ["supabase", "render_connector", "firecrawl"]


def build_runtime_status_snapshot(
    *,
    service_name,
    service_id,
    branch,
    git_head_sha,
    ci_sha,
    ci_status,
    render_live_sha,
    render_deploy_id,
    render_status,
    observed_at,
    source,
):
    required = {
        "service_name": service_name,
        "service_id": service_id,
        "branch": branch,
        "git_head_sha": git_head_sha,
        "ci_sha": ci_sha,
        "render_live_sha": render_live_sha,
        "render_deploy_id": render_deploy_id,
        "observed_at": observed_at,
        "source": source,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ValueError(f"missing runtime status fields: {', '.join(missing)}")

    deployment_consistent = (
        ci_status == "success"
        and render_status == "live"
        and git_head_sha == ci_sha == render_live_sha
    )

    return {
        "status": (
            "runtime_status_verified"
            if deployment_consistent
            else "runtime_status_inconsistent"
        ),
        "service_name": service_name,
        "service_id": service_id,
        "branch": branch,
        "git_head_sha": git_head_sha,
        "ci_sha": ci_sha,
        "ci_status": ci_status,
        "render_live_sha": render_live_sha,
        "render_deploy_id": render_deploy_id,
        "render_status": render_status,
        "deployment_consistent": deployment_consistent,
        "observed_at": observed_at,
        "source": source,
        "source_priority": list(SOURCE_PRIORITY),
        "firecrawl_required": not deployment_consistent,
    }
