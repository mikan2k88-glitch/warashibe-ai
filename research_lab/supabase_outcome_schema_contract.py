"""Preflight schema contract for the opt-in Supabase outcome writer.

This check does not connect to a database or modify its schema.
"""


def assess(columns):
    by_name = {column["column_name"]: column for column in columns}
    issues = []
    required = {"id", "opportunity_key", "sold", "days_to_outcome"}
    if not required.issubset(by_name):
        issues.append("missing_required_columns")
    identifier = by_name.get("id")
    if identifier and identifier.get("column_default") is None:
        issues.append("id_has_no_default")
    days = by_name.get("days_to_outcome")
    if days and days.get("data_type") != "integer":
        issues.append("unexpected_days_type")
    return {"write_ready": not issues, "issues": issues}
