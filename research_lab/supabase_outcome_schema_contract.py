"""Offline preflight contract for the opt-in Supabase outcome writer."""


def assess(columns):
    by_name = {column["column_name"]: column for column in columns}
    issues = []
    required = {"id", "opportunity_key", "sold", "days_to_outcome"}
    if not required.issubset(by_name):
        issues.append("missing_required_columns")
    identifier = by_name.get("id")
    if identifier and not (
        identifier.get("column_default") is not None
        or identifier.get("is_identity") == "YES"
    ):
        issues.append("id_has_no_generation")
    days = by_name.get("days_to_outcome")
    if days and days.get("data_type") != "integer":
        issues.append("unexpected_days_type")
    return {"write_ready": not issues, "issues": issues}
