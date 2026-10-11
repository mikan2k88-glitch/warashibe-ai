from __future__ import annotations


def assess_provider_health(*, fetched: int, normalized: int, duplicates: int, errors: list[str] | None = None) -> dict:
    errors = list(errors or [])
    if errors and normalized == 0:
        status = "blocked"
    elif errors or duplicates > 0:
        status = "degraded"
    else:
        status = "healthy"
    return {
        "status": status,
        "fetched": int(fetched),
        "normalized": int(normalized),
        "duplicates": int(duplicates),
        "errors": errors,
        "read_only": True,
        "live_execution_allowed": False,
    }
