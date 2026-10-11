from __future__ import annotations

import time


class ReadRateLimiter:
    def __init__(self, min_interval_seconds: float = 1.0):
        self.min_interval_seconds = max(0.0, float(min_interval_seconds))
        self._last_call = None

    def wait(self):
        now = time.monotonic()
        if self._last_call is not None:
            elapsed = now - self._last_call
            remaining = self.min_interval_seconds - elapsed
            if remaining > 0:
                time.sleep(remaining)
        self._last_call = time.monotonic()
