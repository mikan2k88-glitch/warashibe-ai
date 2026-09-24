"""Offline tests for the Supabase schema dry run."""

from research_lab.supabase_schema_dry_run_validation import (
    DRY_RUN_VERSION,
    validate_schema_dry_run,
)


def main():
    assert DRY_RUN_VERSION == "0.1"
    result = validate_schema_dry_run()
    assert result == {
        "valid": True,
        "table_count": 2,
        "writes_enabled": False,
        "external_tables_touched": False,
    }
    print("Supabase schema dry-run validation passed")


if __name__ == "__main__":
    main()
