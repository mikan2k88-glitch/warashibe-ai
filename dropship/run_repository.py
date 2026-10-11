from __future__ import annotations


RUN_TABLE = "dropship_research_runs"


class MemoryResearchRunRepository:
    def __init__(self):
        self.rows = []

    def append(self, row: dict) -> dict:
        item = dict(row)
        self.rows.append(item)
        return item


class SupabaseResearchRunRepository:
    def __init__(self, client, table: str = RUN_TABLE):
        if client is None:
            raise ValueError("client is required")
        self.client = client
        self.table = table

    def append(self, row: dict) -> dict:
        if not row.get("sha256"):
            raise ValueError("run record digest is required")
        response = self.client.table(self.table).insert(dict(row)).execute()
        rows = response.data or []
        if not rows:
            raise RuntimeError("research run insert returned no row")
        return dict(rows[0])
