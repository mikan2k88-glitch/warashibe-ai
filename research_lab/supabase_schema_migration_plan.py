"""Offline migration plan for future Warashibe Supabase tables.

This module is documentation-as-code only. It performs no SQL execution and
contains no credentials. The plan is intentionally ordered so a future human-
approved migration can create isolated Warashibe tables without touching the
existing video application's tables.
"""

MIGRATION_PLAN_VERSION = "0.1"

STEPS = (
    {
        "order": 1,
        "action": "create_table",
        "table": "warashibe_sale_outcomes",
        "destructive": False,
        "requires_human_approval": True,
    },
    {
        "order": 2,
        "action": "enable_rls",
        "table": "warashibe_sale_outcomes",
        "destructive": False,
        "requires_human_approval": True,
    },
    {
        "order": 3,
        "action": "restrict_public_anon",
        "table": "warashibe_sale_outcomes",
        "destructive": False,
        "requires_human_approval": True,
    },
    {
        "order": 4,
        "action": "create_table",
        "table": "warashibe_market_evidence",
        "destructive": False,
        "requires_human_approval": True,
    },
    {
        "order": 5,
        "action": "enable_rls",
        "table": "warashibe_market_evidence",
        "destructive": False,
        "requires_human_approval": True,
    },
    {
        "order": 6,
        "action": "restrict_public_anon",
        "table": "warashibe_market_evidence",
        "destructive": False,
        "requires_human_approval": True,
    },
)

PROTECTED_EXISTING_TABLES = ("videos",)


def validate_migration_plan():
    orders = [step["order"] for step in STEPS]
    assert orders == list(range(1, len(STEPS) + 1))
    assert all(step["requires_human_approval"] is True for step in STEPS)
    assert all(step["destructive"] is False for step in STEPS)
    assert all(step["table"].startswith("warashibe_") for step in STEPS)
    assert not {step["table"] for step in STEPS}.intersection(
        PROTECTED_EXISTING_TABLES
    )

    per_table = {}
    for step in STEPS:
        per_table.setdefault(step["table"], []).append(step["action"])

    for actions in per_table.values():
        assert actions == [
            "create_table",
            "enable_rls",
            "restrict_public_anon",
        ]

    return True
