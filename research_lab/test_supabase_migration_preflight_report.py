"""Offline tests for the Supabase migration preflight report."""

from research_lab.supabase_migration_preflight_report import (
    PREFLIGHT_REPORT_VERSION,
    build_preflight_report,
)


def main():
    report = build_preflight_report()

    assert PREFLIGHT_REPORT_VERSION == "0.1"
    assert report == {
        "version": "0.1",
        "technical_checks_passed": True,
        "human_approval_required": True,
        "human_approval_present": False,
        "execution_allowed": False,
        "writes_enabled": False,
        "sql_executed": False,
        "external_tables_touched": False,
        "status": "awaiting_human_approval",
    }

    print("Supabase migration preflight report tests passed")


if __name__ == "__main__":
    main()
