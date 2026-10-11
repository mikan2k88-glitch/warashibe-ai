from __future__ import annotations

from .ops_status import build_ops_status
from .supabase_persistence import load_observation_history, load_recent_runs


def build_persistent_ops_status(client, *, observation_limit: int = 1000, run_limit: int = 100) -> dict:
    errors = []
    observations = []
    runs = []

    try:
        observations = load_observation_history(client, limit=observation_limit)
    except Exception as exc:
        errors.append({"stage": "load_observations", "error": str(exc)})

    try:
        runs = load_recent_runs(client, limit=run_limit)
    except Exception as exc:
        errors.append({"stage": "load_runs", "error": str(exc)})

    status = build_ops_status(observations, runs)
    return {
        **status,
        "database_observation_count": len(observations),
        "database_run_count": len(runs),
        "database_errors": errors,
        "database_read_ok": not errors,
        "live_execution_allowed": False,
    }
