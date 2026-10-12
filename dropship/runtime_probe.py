from __future__ import annotations

from datetime import datetime, timezone
import os

import requests

from .dll_concierge_client import DEFAULT_BASE_URL, REGISTRY_PATH


DEFAULT_WARASHIBE_URL = "https://warashibe-ai.onrender.com"


def _probe_json(session, url: str, *, timeout: int) -> dict:
    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        return {
            "status": "ok",
            "url": url,
            "payload": payload,
        }
    except Exception as exc:
        return {
            "status": "unavailable",
            "url": url,
            "error": str(exc),
        }


def run_runtime_probe(*, session=None, timeout: int = 60) -> dict:
    session = session or requests
    warashibe_base = os.environ.get(
        "WARASHIBE_RUNTIME_URL",
        DEFAULT_WARASHIBE_URL,
    ).rstrip("/")
    dll_base = os.environ.get(
        "DLL_CONCIERGE_BASE_URL",
        DEFAULT_BASE_URL,
    ).rstrip("/")

    warashibe = _probe_json(
        session,
        f"{warashibe_base}/dropship/health",
        timeout=timeout,
    )
    dll = _probe_json(
        session,
        f"{dll_base}{REGISTRY_PATH}",
        timeout=timeout,
    )

    warashibe_ok = (
        warashibe["status"] == "ok"
        and isinstance(warashibe.get("payload"), dict)
        and warashibe["payload"].get("live_execution_allowed") is False
    )
    dll_ok = dll["status"] == "ok"

    return {
        "status": "runtime_probe_ok" if warashibe_ok and dll_ok else "runtime_probe_degraded",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "warashibe": warashibe,
        "dll_concierge": dll,
        "warashibe_safe_boundary_verified": warashibe_ok,
        "dll_registry_reachable": dll_ok,
        "commerce_write_performed": False,
        "live_execution_allowed": False,
    }
