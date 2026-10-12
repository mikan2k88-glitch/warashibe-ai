from __future__ import annotations

from dataclasses import dataclass


AUTH_HINTS = ("401", "403", "unauthorized", "forbidden", "invalid token", "expired")
RATE_HINTS = ("429", "rate limit", "too many requests", "quota")
TRANSIENT_HINTS = ("timeout", "timed out", "connection", "502", "503", "504")


def classify_provider_error(error: str) -> dict:
    text = str(error or "").lower()
    if any(hint in text for hint in AUTH_HINTS):
        kind = "auth"
        retry_allowed = False
    elif any(hint in text for hint in RATE_HINTS):
        kind = "rate_limit"
        retry_allowed = True
    elif any(hint in text for hint in TRANSIENT_HINTS):
        kind = "transient"
        retry_allowed = True
    else:
        kind = "unknown"
        retry_allowed = False
    return {
        "kind": kind,
        "retry_allowed": retry_allowed,
        "commerce_write": False,
    }


def summarize_handshake(handshake: dict) -> dict:
    providers = [handshake.get("cj") or {}, handshake.get("ebay") or {}]
    failures = []
    ready = 0
    for row in providers:
        status = row.get("status")
        if status == "ok":
            ready += 1
        elif status == "failed":
            failures.append({
                "provider": row.get("provider"),
                "diagnostic": classify_provider_error(row.get("error") or ""),
            })
    return {
        "status": "provider_diagnostics_ready",
        "ready_provider_count": ready,
        "failure_count": len(failures),
        "failures": failures,
        "shadow_collection_allowed": ready == 2,
        "live_execution_allowed": False,
    }
