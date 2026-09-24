"""Offline client-integration contract for future Warashibe Supabase access.

No client is created and no environment variable is read here. The already
proven health path remains read-only; future persistence stays disabled until a
human-approved schema and policy migration exists.
"""

CLIENT_INTEGRATION_VERSION = "0.1"

PATHS = {
    "runtime_health": {
        "mode": "read_only",
        "table": "videos",
        "allowed_operations": ("select",),
        "writes_enabled": False,
    },
    "outcome_persistence": {
        "mode": "future_server_only",
        "table": "warashibe_sale_outcomes",
        "allowed_operations": (),
        "writes_enabled": False,
    },
    "market_evidence_persistence": {
        "mode": "future_server_only",
        "table": "warashibe_market_evidence",
        "allowed_operations": (),
        "writes_enabled": False,
    },
}

SECRET_RULES = {
    "read_from_environment_only": True,
    "return_secret": False,
    "log_secret": False,
    "browser_exposure": False,
}


def validate_client_integration():
    health = PATHS["runtime_health"]
    assert health["allowed_operations"] == ("select",)
    assert health["writes_enabled"] is False

    for name in ("outcome_persistence", "market_evidence_persistence"):
        path = PATHS[name]
        assert path["allowed_operations"] == ()
        assert path["writes_enabled"] is False
        assert path["mode"] == "future_server_only"

    assert SECRET_RULES["read_from_environment_only"] is True
    assert SECRET_RULES["return_secret"] is False
    assert SECRET_RULES["log_secret"] is False
    assert SECRET_RULES["browser_exposure"] is False
    return True
