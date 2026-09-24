"""Offline tests for the Supabase schema migration plan."""

from research_lab.supabase_schema_migration_plan import (
    MIGRATION_PLAN_VERSION,
    PROTECTED_EXISTING_TABLES,
    STEPS,
    validate_migration_plan,
)


def main():
    assert MIGRATION_PLAN_VERSION == "0.1"
    assert validate_migration_plan() is True
    assert PROTECTED_EXISTING_TABLES == ("videos",)
    assert len(STEPS) == 6
    assert {step["table"] for step in STEPS} == {
        "warashibe_sale_outcomes",
        "warashibe_market_evidence",
    }
    assert all(step["requires_human_approval"] for step in STEPS)
    assert all(step["destructive"] is False for step in STEPS)

    print("Supabase schema migration plan tests passed")


if __name__ == "__main__":
    main()
