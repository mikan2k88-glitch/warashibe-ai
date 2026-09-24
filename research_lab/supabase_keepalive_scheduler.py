"""Read-only Supabase keep-alive scheduler for the existing web service.

Runs at most once per interval in each process. No background thread is created.
Logs only a coarse success/failure marker; credentials and exception details are
never logged.
"""

import logging
import os
import time

from research_lab.supabase_runtime_smoke import runtime_readonly_smoke

_INTERVAL = int(os.environ.get("WARASHIBE_SUPABASE_KEEPALIVE_SECONDS", "86400"))
_last_attempt = 0.0
_logger = logging.getLogger(__name__)


def maybe_run_keepalive(*, now=None, check=None):
    global _last_attempt
    current = time.monotonic() if now is None else float(now)
    if current - _last_attempt < _INTERVAL:
        return False
    _last_attempt = current
    checker = runtime_readonly_smoke if check is None else check
    result = checker()
    if result.get("read_ok") is True:
        _logger.warning("supabase_keepalive=ok")
    else:
        _logger.warning("supabase_keepalive=failed")
    return True
