"""Offline schema contract for a future shared Supabase project.

This module performs no database calls and changes no external resources.
It defines the minimum Warashibe-owned tables and security expectations so the
project can coexist with unrelated applications such as the existing video app.
"""

WARASHIBE_SCHEMA_VERSION = "0.1"

TABLES = {
    "warashibe_sale_outcomes": {
        "owner": "warashibe",
        "columns": (
            "id",
            "opportunity_key",
            "sold",
            "days_to_outcome",
            "created_at",
        ),
        "required": (
            "opportunity_key",
            "sold",
            "created_at",
        ),
        "rls_required": True,
        "public_anon_access": False,
    },
    "warashibe_market_evidence": {
        "owner": "warashibe",
        "columns": (
            "id",
            "source",
            "external_id",
            "identity_key",
            "purchase_price",
            "expected_sale_price",
            "observed_at",
            "metadata",
            "created_at",
        ),
        "required": (
            "source",
            "external_id",
            "purchase_price",
            "expected_sale_price",
            "observed_at",
            "created_at",
        ),
        "rls_required": True,
        "public_anon_access": False,
    },
}

RESERVED_EXTERNAL_TABLES = ("videos",)


def validate_schema_contract():
    names = tuple(TABLES)
    assert len(names) == len(set(names))
    assert all(name.startswith("warashibe_") for name in names)
    assert not set(names).intersection(RESERVED_EXTERNAL_TABLES)

    for name, spec in TABLES.items():
        assert spec["owner"] == "warashibe"
        assert spec["rls_required"] is True
        assert spec["public_anon_access"] is False
        assert set(spec["required"]).issubset(spec["columns"])
        assert "created_at" in spec["columns"]

    outcome = TABLES["warashibe_sale_outcomes"]
    assert {"opportunity_key", "sold", "days_to_outcome"}.issubset(
        outcome["columns"]
    )
    return True
