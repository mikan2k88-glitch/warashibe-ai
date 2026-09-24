"""Offline tests for the Supabase client-integration boundary."""

from research_lab.supabase_client_integration_design import (
    CLIENT_INTEGRATION_VERSION,
    PATHS,
    SECRET_RULES,
    validate_client_integration,
)


def main():
    assert CLIENT_INTEGRATION_VERSION == "0.1"
    assert validate_client_integration() is True

    health = PATHS["runtime_health"]
    assert health["allowed_operations"] == ("select",)
    assert health["writes_enabled"] is False

    for name in ("outcome_persistence", "market_evidence_persistence"):
        assert PATHS[name]["allowed_operations"] == ()
        assert PATHS[name]["writes_enabled"] is False

    assert SECRET_RULES["read_from_environment_only"] is True
    assert SECRET_RULES["return_secret"] is False
    assert SECRET_RULES["log_secret"] is False
    assert SECRET_RULES["browser_exposure"] is False

    print("Supabase client integration design tests passed")


if __name__ == "__main__":
    main()
