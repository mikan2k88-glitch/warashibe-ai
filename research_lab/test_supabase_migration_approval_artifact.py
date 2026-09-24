"""Offline tests for the migration approval artifact."""

from research_lab.supabase_migration_approval_artifact import (
    APPROVAL_ARTIFACT_VERSION,
    build_approval_artifact,
    validate_approval_artifact,
)


def main():
    assert APPROVAL_ARTIFACT_VERSION == "0.1"
    assert validate_approval_artifact() is True

    artifact = build_approval_artifact()
    assert artifact["approval_granted"] is False
    assert artifact["execution_performed"] is False
    assert artifact["credentials_included"] is False
    assert artifact["destructive_operations"] == ()
    assert "create table public.warashibe_sale_outcomes" in artifact["sql_preview"]
    assert "create table public.warashibe_market_evidence" in artifact["sql_preview"]

    print("Supabase migration approval artifact tests passed")


if __name__ == "__main__":
    main()
