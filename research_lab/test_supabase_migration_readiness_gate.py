"""Offline tests for the Supabase migration readiness gate."""

from research_lab.supabase_migration_readiness_gate import (
    READINESS_GATE_VERSION,
    migration_readiness,
    require_migration_approval,
)


def main():
    assert READINESS_GATE_VERSION == "0.1"

    blocked = migration_readiness()
    assert blocked["technically_ready"] is True
    assert blocked["human_approved"] is False
    assert blocked["execution_allowed"] is False
    assert blocked["writes_enabled"] is False
    assert blocked["sql_executed"] is False

    try:
        require_migration_approval()
    except PermissionError:
        pass
    else:
        raise AssertionError("migration must fail closed without approval")

    approved = require_migration_approval(human_approved=True)
    assert approved["execution_allowed"] is True
    assert approved["writes_enabled"] is False
    assert approved["sql_executed"] is False

    print("Supabase migration readiness gate tests passed")


if __name__ == "__main__":
    main()
