"""SQLite-backed research memory with no external dependencies."""

import json
import os
import sqlite3
from datetime import datetime, timezone

DEFAULT_DB_PATH = os.environ.get("WARASHIBE_LAB_DB", "/tmp/warashibe_lab.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    track TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    baseline_json TEXT NOT NULL,
    candidate_json TEXT NOT NULL,
    decision TEXT NOT NULL,
    reason TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_experiments_created_at ON experiments(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_experiments_track ON experiments(track);
"""


class ResearchRepository:
    def __init__(self, path: str = DEFAULT_DB_PATH):
        self.path = path
        self.initialize()

    def connect(self):
        return sqlite3.connect(self.path)

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    def record(self, *, track, title, status, baseline, candidate, decision, reason, notes="") -> int:
        created_at = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            cursor = connection.execute(
                """INSERT INTO experiments
                (created_at, track, title, status, baseline_json, candidate_json, decision, reason, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (created_at, track, title, status, json.dumps(baseline, ensure_ascii=False),
                 json.dumps(candidate, ensure_ascii=False), decision, reason, notes),
            )
            return int(cursor.lastrowid)

    def recent(self, limit: int = 20):
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT * FROM experiments ORDER BY id DESC LIMIT ?", (max(1, min(limit, 200)),)
            ).fetchall()
        return [self._decode(dict(row)) for row in rows]

    def stats(self):
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            total = connection.execute("SELECT COUNT(*) AS n FROM experiments").fetchone()["n"]
            rows = connection.execute(
                "SELECT decision, COUNT(*) AS n FROM experiments GROUP BY decision"
            ).fetchall()
        return {"total": total, "decisions": {row["decision"]: row["n"] for row in rows}}

    @staticmethod
    def _decode(row):
        row["baseline"] = json.loads(row.pop("baseline_json"))
        row["candidate"] = json.loads(row.pop("candidate_json"))
        return row
