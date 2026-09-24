"""Freshness gate for timestamped market observations."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from research_lab.real_market_schema import MarketObservation

FRESHNESS_VERSION = "0.1"


@dataclass(frozen=True)
class FreshnessResult:
    accepted: tuple[MarketObservation, ...]
    rejected: tuple[MarketObservation, ...]
    missing_timestamp: int
    stale: int


def _utc(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError("observed_at must include timezone")
    return dt.astimezone(timezone.utc)


def filter_fresh_observations(
    observations: Iterable[MarketObservation], *, now: datetime | None = None, max_age_seconds: int = 3600
) -> FreshnessResult:
    """Fail closed on missing/invalid/future/stale observation timestamps."""
    if max_age_seconds < 0:
        raise ValueError("max_age_seconds must be >= 0")
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    accepted, rejected = [], []
    missing, stale = 0, 0
    for row in observations:
        if not row.observed_at:
            rejected.append(row); missing += 1; continue
        try:
            observed = _utc(row.observed_at)
        except (TypeError, ValueError):
            rejected.append(row); missing += 1; continue
        age = (now - observed).total_seconds()
        if age < 0 or age > max_age_seconds:
            rejected.append(row); stale += 1; continue
        accepted.append(row)
    return FreshnessResult(tuple(accepted), tuple(rejected), missing, stale)
