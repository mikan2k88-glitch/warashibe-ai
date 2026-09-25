"""One-shot Gemini connectivity probe for the research-lab deployment.

This module never logs or returns the API key. It uses only the Python standard
library so the probe does not introduce a new runtime dependency.
"""

from __future__ import annotations

import json
import os
import time
from urllib import error, parse, request

PRIMARY_MODEL = "gemini-3.8-flash"
FALLBACK_MODELS = ("gemini-3.7-flash", "gemini-3.5-flash")
RETRYABLE_CODES = {408, 429, 500, 502, 503, 504}


def _call_model(api_key: str, model: str, timeout: int = 20) -> tuple[bool, int | None, str]:
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{parse.quote(model, safe='')}:generateContent"
    )
    payload = {
        "contents": [{"parts": [{"text": "Reply with exactly: WARASHIBE_GEMINI_OK"}]}],
        "generationConfig": {"maxOutputTokens": 24, "temperature": 0},
    }
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
            text = (
                body.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
                .strip()
            )
            return text == "WARASHIBE_GEMINI_OK", response.status, text[:120]
    except error.HTTPError as exc:
        return False, exc.code, f"http_{exc.code}"
    except (error.URLError, TimeoutError):
        return False, None, "network_error"


def run_live_probe() -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "status": "skipped",
            "reason": "gemini_api_key_missing",
            "api_key_present": False,
        }

    models = (PRIMARY_MODEL,) + FALLBACK_MODELS
    attempts = []

    for model in models:
        ok, code, detail = _call_model(api_key, model)
        attempts.append({"model": model, "ok": ok, "code": code, "detail": detail})
        if ok:
            return {
                "status": "success",
                "api_key_present": True,
                "selected_model": model,
                "fallback_used": model != PRIMARY_MODEL,
                "attempts": attempts,
            }

        if code not in RETRYABLE_CODES:
            break

        time.sleep(1)

    return {
        "status": "failed",
        "api_key_present": True,
        "selected_model": None,
        "fallback_used": len(attempts) > 1,
        "attempts": attempts,
    }
