"""Read-only Supabase keep-alive scheduler for the existing web service.

Runs at most once per interval in each process. No background thread is created:
a normal request opportunistically triggers the bounded read-only smoke check.
"""

import os
import time

from research_lab.supabase_runtime_smoke import runtime_readonly_smoke

_INTERVAL = int(os.environ.get("WARASHIBE_SUPABASE_KEEPALIVE_SECONDS", "86400"))
_last_attempt = 0.0


def maybe_run_keepalive(*, now=None, check=None):
    global _last_attempt
    current = time.monotonic() if now is None else float(now)
    if current - _last_attempt < _INTERVAL:
        return False
    _last_attempt = current
    checker = runtime_readonly_smoke if check is None else check
    checker()
    return True
