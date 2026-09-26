"""Classify the configured LAB key without logging or exposing its value.

Legacy JWT keys cannot safely be identified by prefix alone.
"""


def classify_key(key):
    if not key:
        return "missing"
    if key.startswith("sb_secret_"):
        return "secret"
    if key.startswith("sb_publishable_"):
        return "publishable"
    return "unknown"


def configured_key_kind(environ):
    key = (environ.get("SUPABASE_SERVICE_ROLE_KEY")
           or environ.get("SUPABASE_SECRET_KEY")
           or environ.get("SUPABASE_KEY"))
    return classify_key(key)
