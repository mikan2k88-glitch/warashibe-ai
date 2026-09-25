"""Offline Gemini adapter policy and response parsing for sandbox experiments.

No network calls are performed here. The module centralizes model order,
retry classification, and robust extraction of non-thought text from Gemini
REST responses before live use is enabled again.
"""

GEMINI_SANDBOX_ADAPTER_VERSION = "0.1"

MODEL_ORDER = (
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
)

RETRYABLE_HTTP_CODES = frozenset({408, 429, 500, 502, 503, 504})
STOP_HTTP_CODES = frozenset({400, 401, 402, 403, 404})


def classify_http_error(code):
    if code in RETRYABLE_HTTP_CODES:
        return "retry_then_fallback"
    if code in STOP_HTTP_CODES:
        return "stop"
    if code is None:
        return "network_failure"
    return "stop"


def extract_response_text(payload):
    """Return visible model text while ignoring thought-only parts."""
    if not isinstance(payload, dict):
        return ""

    chunks = []
    for candidate in payload.get("candidates") or ():
        if not isinstance(candidate, dict):
            continue
        content = candidate.get("content")
        if not isinstance(content, dict):
            continue
        for part in content.get("parts") or ():
            if not isinstance(part, dict):
                continue
            if part.get("thought") is True:
                continue
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                chunks.append(text.strip())
    return "\n".join(chunks).strip()


def build_model_attempt_plan(primary=None):
    """Return a unique primary-first compatible fallback order."""
    primary = primary or MODEL_ORDER[0]
    ordered = [primary]
    ordered.extend(model for model in MODEL_ORDER if model != primary)
    return tuple(ordered)


def evaluate_probe_payload(payload, expected="WARASHIBE_GEMINI_OK"):
    text = extract_response_text(payload)
    return {
        "version": GEMINI_SANDBOX_ADAPTER_VERSION,
        "ok": text.strip() == expected,
        "text_present": bool(text),
        "text": text,
    }


def build_offline_adapter_snapshot():
    return {
        "version": GEMINI_SANDBOX_ADAPTER_VERSION,
        "mode": "offline_sandbox",
        "model_order": MODEL_ORDER,
        "retryable_http_codes": tuple(sorted(RETRYABLE_HTTP_CODES)),
        "network_execution_authorized": False,
        "secret_access_authorized": False,
        "production_change_authorized": False,
        "external_action_authorized": False,
        "requires_live_human_gate": True,
    }
