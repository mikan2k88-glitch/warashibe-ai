from __future__ import annotations

from datetime import datetime, timezone
import os
import time

import requests

from .dll_concierge_client import DEFAULT_BASE_URL, REGISTRY_PATH


def wake_dll_concierge(*, attempts: int = 3, timeout: int = 60, delay_seconds: int = 5) -> dict:
    base_url = os.environ.get("DLL_CONCIERGE_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    started = time.monotonic()
    errors = []

    for attempt in range(1, max(1, attempts) + 1):
        try:
            response = requests.get(
                f"{base_url}{REGISTRY_PATH}",
                timeout=timeout,
            )
            response.raise_for_status()
            response.json()
            return {
                "status": "awake",
                "attempts": attempt,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "checked_at": datetime.now(timezone.utc).isoformat(),
                "read_only": True,
            }
        except (requests.RequestException, ValueError) as exc:
            errors.append(str(exc))
            if attempt < attempts:
                time.sleep(max(0, delay_seconds))

    return {
        "status": "unavailable",
        "attempts": max(1, attempts),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "errors": errors[-3:],
        "read_only": True,
    }
