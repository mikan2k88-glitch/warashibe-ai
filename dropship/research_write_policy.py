from __future__ import annotations


ALLOWED_APPEND_ONLY_TABLES = {
    "dropship_observations",
    "dropship_audit_log",
    "dropship_research_snapshots",
}


def authorize_research_write(*, table: str, operation: str) -> dict:
    allowed = operation == "insert" and table in ALLOWED_APPEND_ONLY_TABLES
    return {
        "allowed": allowed,
        "table": table,
        "operation": operation,
        "append_only": allowed,
        "commerce_write": False,
        "reason": None if allowed else "research_write_not_allowlisted",
    }
