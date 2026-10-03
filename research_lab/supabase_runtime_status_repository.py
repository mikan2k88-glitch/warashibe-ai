"""Supabase append-only repository for verified runtime status snapshots."""

TABLE_NAME = "warashibe_runtime_status"


class SupabaseRuntimeStatusRepository:
    def __init__(self, client, table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client = client
        self.table = table

    def latest(self, service_name, branch):
        response = (
            self.client.table(self.table)
            .select(
                "snapshot_key,service_name,service_id,branch,git_head_sha,"
                "ci_sha,ci_status,render_live_sha,render_deploy_id,"
                "render_status,deployment_consistent,source,observed_at"
            )
            .eq("service_name", service_name)
            .eq("branch", branch)
            .order("observed_at", desc=True)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return dict(rows[0]) if rows else None

    def append(self, snapshot):
        if not isinstance(snapshot, dict):
            raise ValueError("snapshot must be a mapping")
        if snapshot.get("status") not in {
            "runtime_status_verified",
            "runtime_status_inconsistent",
        }:
            raise ValueError("runtime status contract required")

        key = snapshot.get("snapshot_key")
        if not key:
            key = (
                f"{snapshot.get('service_id')}:{snapshot.get('branch')}:"
                f"{snapshot.get('git_head_sha')}:{snapshot.get('render_deploy_id')}"
            )

        response = self.client.table(self.table).insert({
            "snapshot_key": key,
            "service_name": snapshot.get("service_name"),
            "service_id": snapshot.get("service_id"),
            "branch": snapshot.get("branch"),
            "git_head_sha": snapshot.get("git_head_sha"),
            "ci_sha": snapshot.get("ci_sha"),
            "ci_status": snapshot.get("ci_status"),
            "render_live_sha": snapshot.get("render_live_sha"),
            "render_deploy_id": snapshot.get("render_deploy_id"),
            "render_status": snapshot.get("render_status"),
            "deployment_consistent": snapshot.get("deployment_consistent"),
            "source": snapshot.get("source"),
            "snapshot": dict(snapshot),
            "observed_at": snapshot.get("observed_at"),
        }).execute()
        rows = response.data or []
        if not rows:
            raise RuntimeError("runtime status insert returned no row")
        return dict(rows[0])
