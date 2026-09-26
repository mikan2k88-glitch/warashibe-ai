"""Opt-in, read-only diagnostic for the Warashibe-owned Supabase tables.

Run manually: python -m research_lab.supabase_warashibe_read_probe
No probe is run on import, web requests, or CI. Credentials are never printed.
"""
import json
import os

TABLES = ("warashibe_sale_outcomes", "warashibe_market_evidence")


def probe(*, client_factory=None, environ=None):
    env = os.environ if environ is None else environ
    url = env.get("SUPABASE_URL")
    key = env.get("SUPABASE_SERVICE_ROLE_KEY") or env.get("SUPABASE_SECRET_KEY")
    if not url or not key:
        return {"status": "not_configured", "read_ok": False, "tables": {}}
    if client_factory is None:
        from supabase import create_client
        client_factory = create_client
    try:
        client = client_factory(url, key)
    except Exception:
        return {"status": "client_creation_failed", "read_ok": False, "tables": {}}
    checks = {}
    for table in TABLES:
        try:
            response = client.table(table).select("id").limit(1).execute()
            checks[table] = "ok" if response is not None else "failed"
        except Exception:
            checks[table] = "failed"
    return {
        "status": "ok" if all(value == "ok" for value in checks.values()) else "read_failed",
        "read_ok": all(value == "ok" for value in checks.values()),
        "tables": checks,
    }


def main():
    result = probe()
    print(json.dumps(result, sort_keys=True))
    return 0 if result["read_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
