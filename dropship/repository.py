from __future__ import annotations


OBSERVATION_TABLE = "dropship_observations"
AUDIT_TABLE = "dropship_audit_log"
SNAPSHOT_TABLE = "dropship_research_snapshots"


class MemoryAppendOnlyRepository:
    def __init__(self):
        self.observations = []
        self.audit_records = []
        self.snapshots = []

    def append_observation(self, row: dict) -> dict:
        item = dict(row)
        self.observations.append(item)
        return item

    def append_audit(self, row: dict) -> dict:
        item = dict(row)
        self.audit_records.append(item)
        return item

    def append_snapshot(self, row: dict) -> dict:
        item = dict(row)
        self.snapshots.append(item)
        return item


class SupabaseDropshipRepository:
    """Append-only Supabase repository.

    A configured Supabase client must be injected by the application.
    This module never creates clients, reads secrets, or enables live commerce.
    """

    def __init__(self, client):
        if client is None:
            raise ValueError("client is required")
        self.client = client

    def _insert(self, table: str, row: dict) -> dict:
        response = self.client.table(table).insert(dict(row)).execute()
        rows = response.data or []
        if not rows:
            raise RuntimeError(f"{table} insert returned no row")
        return dict(rows[0])

    def append_observation(self, row: dict) -> dict:
        if not row.get("product_key"):
            raise ValueError("product_key is required")
        return self._insert(OBSERVATION_TABLE, row)

    def append_audit(self, row: dict) -> dict:
        if not row.get("sha256"):
            raise ValueError("audit digest is required")
        return self._insert(AUDIT_TABLE, row)

    def append_snapshot(self, row: dict) -> dict:
        if not row.get("sha256"):
            raise ValueError("snapshot digest is required")
        return self._insert(SNAPSHOT_TABLE, row)
