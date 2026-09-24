"""Read-only Supabase runtime connectivity smoke check.

Credentials are read from environment variables but never returned or logged.
The check performs only a bounded SELECT and never creates, updates, or deletes
database objects or rows.
"""

import os


def runtime_readonly_smoke(*, client_factory=None, table="videos"):
    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_PUBLISHABLE_KEY")
        or os.environ.get("SUPABASE_KEY")
    )
    if not url or not key:
        return {
            "configured": False,
            "client_created": False,
            "read_ok": False,
            "reason": "missing_environment",
        }

    if client_factory is None:
        from supabase import create_client
        client_factory = create_client

    try:
        client = client_factory(url, key)
    except Exception:
        return {
            "configured": True,
            "client_created": False,
            "read_ok": False,
            "reason": "client_creation_failed",
        }

    try:
        response = client.table(table).select("id").limit(1).execute()
        row_count = len(response.data or [])
    except Exception:
        return {
            "configured": True,
            "client_created": True,
            "read_ok": False,
            "reason": "readonly_query_failed",
        }

    return {
        "configured": True,
        "client_created": True,
        "read_ok": True,
        "reason": "ok",
        "row_count": row_count,
    }
