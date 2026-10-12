from __future__ import annotations

import os


def check_credential_env(names: list[str]) -> dict:
    checks = {name: bool(os.environ.get(name, "").strip()) for name in names}
    return {
        "configured": checks,
        "configured_count": sum(1 for value in checks.values() if value),
        "required_count": len(checks),
        "all_configured": all(checks.values()) if checks else True,
        "secret_values_exposed": False,
    }
