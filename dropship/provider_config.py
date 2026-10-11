from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    url: str
    mode: str = "read_only"
    timeout_seconds: int = 30
    min_interval_seconds: float = 1.0
    max_items: int = 200

    def validate(self) -> dict:
        reasons = []
        if self.mode != "read_only":
            reasons.append("provider_must_be_read_only")
        if not self.url.startswith(("http://", "https://")):
            reasons.append("provider_url_must_be_http")
        if self.timeout_seconds <= 0:
            reasons.append("timeout_must_be_positive")
        if self.min_interval_seconds < 0:
            reasons.append("min_interval_must_be_non_negative")
        if self.max_items <= 0:
            reasons.append("max_items_must_be_positive")
        return {"valid": not reasons, "reasons": reasons, "config": asdict(self)}
