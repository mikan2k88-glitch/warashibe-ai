"""Explicitly opt-in, single-row write/read/delete diagnostic.

Never runs on import or a web request. Caller supplies a trusted client.
Only the unique probe row is eligible for cleanup. No raw errors or secrets logged.
"""
from uuid import uuid4

TABLE = "warashibe_sale_outcomes"
PREFIX = "__warashibe_write_probe__:"


def probe(client, *, token=None):
    marker = PREFIX + (token or uuid4().hex)
    inserted_id = None
    status = "write_failed"
    cleanup_ok = False
    try:
        response = client.table(TABLE).insert({
            "opportunity_key": marker,
            "sold": False,
            "days_to_outcome": 0,
        }).execute()
        rows = response.data or []
        if len(rows) != 1 or rows[0].get("opportunity_key") != marker:
            status = "write_unconfirmed"
        else:
            inserted_id = rows[0].get("id")
            if inserted_id is None:
                status = "id_unavailable"
            else:
                read = (client.table(TABLE).select("id,opportunity_key")
                        .eq("id", inserted_id).eq("opportunity_key", marker).execute())
                status = ("read_ok" if len(read.data or []) == 1
                          and read.data[0].get("opportunity_key") == marker
                          else "read_failed")
    except Exception:
        status = "write_or_read_failed"
    finally:
        # Never delete a row without both its returned ID and unique marker.
        if inserted_id is not None:
            try:
                client.table(TABLE).delete().eq("id", inserted_id).eq(
                    "opportunity_key", marker
                ).execute()
                verify = (client.table(TABLE).select("id").eq("id", inserted_id)
                          .eq("opportunity_key", marker).execute())
                cleanup_ok = len(verify.data or []) == 0
            except Exception:
                cleanup_ok = False
    return {"status": "ok" if status == "read_ok" and cleanup_ok else status,
            "write_read_ok": status == "read_ok",
            "cleanup_ok": cleanup_ok,
            "manual_review_required": inserted_id is None or not cleanup_ok}
