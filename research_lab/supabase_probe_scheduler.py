"""Run the read-only Warashibe table probe once per web process.

Only coarse statuses are logged. Never log URLs, keys, exceptions or row data.
"""
import logging
import threading

from research_lab.supabase_warashibe_read_probe import probe

_lock = threading.Lock()
_attempted = False
_logger = logging.getLogger(__name__)


def maybe_run_probe(*, check=None):
    global _attempted
    with _lock:
        if _attempted:
            return False
        _attempted = True
    try:
        result = (probe if check is None else check)()
        status = result.get("status")
        if status not in {"ok", "read_failed", "not_configured", "client_creation_failed"}:
            status = "failed"
    except Exception:
        status = "failed"
    _logger.warning("warashibe_supabase_read_probe=%s", status)
    return True
