"""Cross-check the future Supabase migration entirely offline.

The dry run validates that schema, migration, SQL, policy, and client contracts
agree before any real DDL or permission change can be considered.
"""

from research_lab.supabase_client_integration_design import PATHS
from research_lab.supabase_schema_contract import TABLES
from research_lab.supabase_schema_migration_plan import (
    PROTECTED_EXISTING_TABLES,
    STEPS,
)
from research_lab.supabase_schema_policy_contract import ROLE_POLICIES
from research_lab.supabase_schema_sql_rendering import render_full_migration_sql

DRY_RUN_VERSION = "0.1"


def validate_schema_dry_run():
    tables = set(TABLES)
    planned_tables = {step["table"] for step in STEPS}
    future_client_tables = {
        PATHS["outcome_persistence"]["table"],
        PATHS["market_evidence_persistence"]["table"],
    }

    assert tables == planned_tables == future_client_tables
    assert not tables.intersection(PROTECTED_EXISTING_TABLES)

    sql = render_full_migration_sql().lower()
    for table in tables:
        assert f"create table public.{table}" in sql
        assert f"alter table public.{table} enable row level security" in sql
        assert f"revoke all on table public.{table} from anon" in sql

    assert "public.videos" not in sql
    assert all(
        permission is False
        for permissions in ROLE_POLICIES.values()
        for permission in permissions.values()
    )
    assert PATHS["outcome_persistence"]["writes_enabled"] is False
    assert PATHS["market_evidence_persistence"]["writes_enabled"] is False

    forbidden = ("drop table", "truncate", "delete from", "grant all")
    assert not any(token in sql for token in forbidden)
    return {
        "valid": True,
        "table_count": len(tables),
        "writes_enabled": False,
        "external_tables_touched": False,
    }
