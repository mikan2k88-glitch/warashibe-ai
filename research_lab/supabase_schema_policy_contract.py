"""Offline access-policy contract for future Warashibe Supabase tables.

No SQL is executed here. The contract is deliberately fail-closed: public anon
access is denied, and any future application role must be granted only the
minimum operations required by a separately reviewed integration.
"""

from research_lab.supabase_schema_contract import TABLES

POLICY_CONTRACT_VERSION = "0.1"

ROLE_POLICIES = {
    "anon": {
        "select": False,
        "insert": False,
        "update": False,
        "delete": False,
    },
    "authenticated": {
        "select": False,
        "insert": False,
        "update": False,
        "delete": False,
    },
}

SERVER_ROLE_RULES = {
    "secret_required": True,
    "browser_exposure_allowed": False,
    "log_secret_allowed": False,
}


def validate_policy_contract():
    assert set(ROLE_POLICIES) == {"anon", "authenticated"}
    for permissions in ROLE_POLICIES.values():
        assert set(permissions) == {"select", "insert", "update", "delete"}
        assert all(value is False for value in permissions.values())

    assert SERVER_ROLE_RULES == {
        "secret_required": True,
        "browser_exposure_allowed": False,
        "log_secret_allowed": False,
    }
    assert all(spec["rls_required"] is True for spec in TABLES.values())
    assert all(spec["public_anon_access"] is False for spec in TABLES.values())
    return True
