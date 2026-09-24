"""Build a secret-safe human-review artifact for a future migration.

The artifact describes exactly what would be approved. It contains no
credentials, performs no SQL execution, and does not itself grant approval.
"""

from research_lab.supabase_schema_contract import TABLES
from research_lab.supabase_schema_sql_rendering import render_full_migration_sql

APPROVAL_ARTIFACT_VERSION = "0.1"


def build_approval_artifact():
    sql = render_full_migration_sql()
    return {
        "version": APPROVAL_ARTIFACT_VERSION,
        "scope": "warashibe_supabase_schema",
        "tables": tuple(TABLES),
        "protected_existing_tables": ("videos",),
        "operations": ("create_table", "enable_rls", "revoke_anon"),
        "destructive_operations": (),
        "writes_to_existing_rows": False,
        "credentials_included": False,
        "sql_preview": sql,
        "approval_granted": False,
        "execution_performed": False,
    }


def validate_approval_artifact():
    artifact = build_approval_artifact()
    assert set(artifact["tables"]) == {
        "warashibe_sale_outcomes",
        "warashibe_market_evidence",
    }
    assert artifact["protected_existing_tables"] == ("videos",)
    assert artifact["destructive_operations"] == ()
    assert artifact["writes_to_existing_rows"] is False
    assert artifact["credentials_included"] is False
    assert artifact["approval_granted"] is False
    assert artifact["execution_performed"] is False

    sql = artifact["sql_preview"].lower()
    assert "public.videos" not in sql
    assert "drop table" not in sql
    assert "truncate" not in sql
    assert "delete from" not in sql
    return True
