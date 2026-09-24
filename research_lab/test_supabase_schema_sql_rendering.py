"""Offline tests for Supabase schema SQL rendering."""

from research_lab.supabase_schema_sql_rendering import (
    SQL_RENDERER_VERSION,
    render_create_table_sql,
    render_full_migration_sql,
    render_security_sql,
)


def main():
    assert SQL_RENDERER_VERSION == "0.1"

    outcomes = render_create_table_sql("warashibe_sale_outcomes")
    assert "create table public.warashibe_sale_outcomes" in outcomes
    assert "opportunity_key text not null" in outcomes
    assert "sold boolean not null" in outcomes
    assert "days_to_outcome integer" in outcomes

    evidence = render_create_table_sql("warashibe_market_evidence")
    assert "create table public.warashibe_market_evidence" in evidence
    assert "metadata jsonb" in evidence
    assert "check (purchase_price >= 0)" in evidence
    assert "check (expected_sale_price >= 0)" in evidence

    security = render_security_sql("warashibe_sale_outcomes")
    assert "enable row level security" in security
    assert "revoke all on table public.warashibe_sale_outcomes from anon" in security

    full = render_full_migration_sql()
    assert "public.videos" not in full
    assert "drop table" not in full.lower()
    assert "delete from" not in full.lower()
    assert "truncate" not in full.lower()

    try:
        render_create_table_sql("videos")
    except ValueError:
        pass
    else:
        raise AssertionError("protected external table was renderable")

    print("Supabase schema SQL rendering tests passed")


if __name__ == "__main__":
    main()
