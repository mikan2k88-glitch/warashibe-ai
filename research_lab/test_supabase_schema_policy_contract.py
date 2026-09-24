"""Offline tests for the fail-closed Supabase policy contract."""

from research_lab.supabase_schema_policy_contract import (
    POLICY_CONTRACT_VERSION,
    ROLE_POLICIES,
    SERVER_ROLE_RULES,
    validate_policy_contract,
)


def main():
    assert POLICY_CONTRACT_VERSION == "0.1"
    assert validate_policy_contract() is True

    for role in ("anon", "authenticated"):
        assert role in ROLE_POLICIES
        assert all(value is False for value in ROLE_POLICIES[role].values())

    assert SERVER_ROLE_RULES["secret_required"] is True
    assert SERVER_ROLE_RULES["browser_exposure_allowed"] is False
    assert SERVER_ROLE_RULES["log_secret_allowed"] is False

    print("Supabase schema policy contract tests passed")


if __name__ == "__main__":
    main()
