"""Offline validation for the Warashibe Supabase schema contract."""

from research_lab.supabase_schema_contract import (
    RESERVED_EXTERNAL_TABLES,
    TABLES,
    WARASHIBE_SCHEMA_VERSION,
    validate_schema_contract,
)


def main():
    assert WARASHIBE_SCHEMA_VERSION == "0.1"
    assert validate_schema_contract() is True
    assert "videos" in RESERVED_EXTERNAL_TABLES
    assert "videos" not in TABLES
    assert set(TABLES) == {
        "warashibe_sale_outcomes",
        "warashibe_market_evidence",
    }
    for spec in TABLES.values():
        assert spec["rls_required"] is True
        assert spec["public_anon_access"] is False

    print("Supabase schema contract tests passed")


if __name__ == "__main__":
    main()
