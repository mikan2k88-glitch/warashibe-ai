"""Aggregate offline Supabase migration checks into one preflight report.

This report is informational only. It cannot approve or execute a migration.
"""

from research_lab.supabase_migration_approval_artifact import validate_approval_artifact
from research_lab.supabase_migration_readiness_gate import migration_readiness
from research_lab.supabase_schema_dry_run_validation import validate_schema_dry_run

PREFLIGHT_REPORT_VERSION = "0.1"


def build_preflight_report():
    dry_run = validate_schema_dry_run()
    artifact_valid = validate_approval_artifact()
    readiness = migration_readiness()

    technical_checks_passed = (
        dry_run["valid"] is True
        and artifact_valid is True
        and readiness["technically_ready"] is True
    )

    return {
        "version": PREFLIGHT_REPORT_VERSION,
        "technical_checks_passed": technical_checks_passed,
        "human_approval_required": True,
        "human_approval_present": readiness["human_approved"],
        "execution_allowed": readiness["execution_allowed"],
        "writes_enabled": False,
        "sql_executed": False,
        "external_tables_touched": dry_run["external_tables_touched"],
        "status": "awaiting_human_approval" if technical_checks_passed else "blocked",
    }
