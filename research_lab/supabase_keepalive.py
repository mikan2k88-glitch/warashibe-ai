"""Read-only Supabase keep-alive for the research environment.

Uses the same bounded SELECT proven by the runtime smoke test. It never creates,
updates, or deletes database objects or rows and never prints credentials.
"""

import json

from research_lab.supabase_runtime_smoke import runtime_readonly_smoke


def main():
    result = runtime_readonly_smoke()
    safe = {
        "configured": result.get("configured", False),
        "client_created": result.get("client_created", False),
        "read_ok": result.get("read_ok", False),
        "reason": result.get("reason", "unknown"),
    }
    print(json.dumps(safe, sort_keys=True))
    raise SystemExit(0 if safe["read_ok"] else 1)


if __name__ == "__main__":
    main()
