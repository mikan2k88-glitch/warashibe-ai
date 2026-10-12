from __future__ import annotations

import os
import time

import requests


DEFAULT_BASE_URL = "https://dll-concierge.onrender.com"
REGISTRY_PATH = "/factory/v5.3/registry"


def fetch_registry(*, attempts: int = 3, timeout: int = 60, delay_seconds: int = 5) -> dict | list:
    """Wake DLL Concierge if needed and fetch its v5.3 registry.

    GET is retried because it is read-only. No write/execution endpoint is retried here.
    """
    base_url = os.environ.get("DLL_CONCIERGE_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    last_error = None

    for attempt in range(max(1, attempts)):
        try:
            response = requests.get(f"{base_url}{REGISTRY_PATH}", timeout=timeout)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(max(0, delay_seconds))

    raise RuntimeError(f"DLL Concierge registry unavailable: {last_error}")
