"""Explicit opt-in, one-row Supabase write/read/cleanup diagnostic.

Never runs on import, web requests or CI against a live database.
Caller supplies a trusted client. No raw errors, credentials or row data logged.
"""
from uuid import uuid4

TABLE = "warashibe_sale_outcomes"
PREFIX = "__warashibe_write_probe__:"


def probe(client, *, token=None):
    marker = PREFIX + (token or uuid4().hex)
    status = "write_failed"
    cleanup_ok = False
    try:
        response = client.table(TABLE).insert({
            "opportunity_key": marker,
            "sold": False,
            "days_to_outcome": 0,
        }).execute()
        rows = response.data or []
        read = (client.table(TABLE).select("id,opportunity_key")
                .eq("opportunity_key", marker).execute())
        found = read.data or []
        if len(found) == 1 and found[0].get("opportunity_key") == marker:
            status = "read_ok"
        elif len(rows) == 1:
            status = "read_failed"
        else:
            status = "write_unconfirmed"
    except Exception:
        status = "write_or_read_failed"
    finally:
        try:
            # Unique generated marker restricts deletion to this probe's row.
            client.table(TABLE).delete().eq("opportunity_key", marker).execute()
            verify = (client.table(TABLE).select("id")
                      .eq("opportunity_key", marker).execute())
            cleanup_ok = len(verify.data or []) == 0
        except Exception:
            cleanup_ok = False
    return {"status": "ok" if status == "read_ok" and cleanup_ok else status,
            "write_read_ok": status == "read_ok",
            "cleanup_ok": cleanup_ok,
            "manual_review_required": not cleanup_ok}
