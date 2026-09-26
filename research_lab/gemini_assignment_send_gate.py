"""Durable, fail-closed one-shot assignment gate using a persistent SQLite file.

The caller owns the database path and must use durable storage across process
restarts and deployments. Consuming a gate does not send a request or authorize
any downstream action. An uncertain delivery must never be automatically retried.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


def consume_assignment_gate(database_path, assignment_id, source_run_id):
    """Atomically reserve an assignment ID exactly once; return True only on insert.

    Fail closed on malformed input, database errors, duplicates and conflicts.
    The unique assignment_id prevents replay even with a different source run.
    """
    if (not isinstance(assignment_id, str) or not assignment_id.strip()
            or len(assignment_id) > 256 or not isinstance(source_run_id, str)
            or not source_run_id.strip() or len(source_run_id) > 256):
        return False
    try:
        path = Path(database_path)
        if not path.is_file():
            return False  # Explicit initialization; do not silently create a new ledger.
        with sqlite3.connect(str(path), timeout=5) as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "INSERT INTO assignment_send_gate (assignment_id, source_run_id) VALUES (?, ?)",
                (assignment_id, source_run_id),
            )
            connection.commit()
        return True
    except (OSError, TypeError, ValueError, sqlite3.Error):
        return False


def initialize_assignment_gate(database_path):
    """Explicitly initialize a persistent ledger; do not call on every send."""
    path = Path(database_path)
    if not path.parent.is_dir():
        raise ValueError("ledger_parent_missing")
    with sqlite3.connect(str(path), timeout=5) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS assignment_send_gate ("
            "assignment_id TEXT PRIMARY KEY NOT NULL, "
            "source_run_id TEXT NOT NULL, "
            "consumed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
        connection.commit()


def make_assignment_gate(database_path, assignment_id, source_run_id):
    """Return the zero-argument consumer expected by send_assignment_once."""
    return lambda: consume_assignment_gate(database_path, assignment_id, source_run_id)
