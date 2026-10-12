from __future__ import annotations

import os


def assess_kill_switch(*, explicit: bool | None = None) -> dict:
    env_value = os.environ.get("DROPSHIP_KILL_SWITCH", "").strip().lower()
    env_enabled = env_value in {"1", "true", "yes", "on"}
    enabled = env_enabled if explicit is None else bool(explicit)
    return {
        "enabled": enabled,
        "source": "environment" if explicit is None else "explicit",
        "limited_live_preparation_allowed": not enabled,
        "live_execution_allowed": False,
    }
