from __future__ import annotations


class ReadOnlyCircuitBreaker:
    def __init__(self, failure_threshold: int = 3):
        self.failure_threshold = max(1, int(failure_threshold))
        self.failures = 0
        self.open = False

    def record_success(self):
        self.failures = 0
        self.open = False

    def record_failure(self):
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.open = True

    def allow_request(self) -> bool:
        return not self.open

    def snapshot(self) -> dict:
        return {
            "failure_threshold": self.failure_threshold,
            "failures": self.failures,
            "open": self.open,
            "read_only": True,
        }
