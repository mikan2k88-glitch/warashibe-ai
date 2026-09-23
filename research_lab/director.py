"""High-level research director for Warashibe AI.

This module does not modify production code. It selects the next broad research
track from structured evidence so experiments can remain separated from main.
"""

from dataclasses import dataclass
from typing import Iterable

from research_lab.config import RESEARCH_TRACKS


@dataclass(frozen=True)
class ResearchSignal:
    track: str
    maturity: float
    blocker_score: float
    expected_value: float

    def priority(self) -> float:
        # Prefer important blockers with high expected research value, while
        # naturally reducing priority as a track matures.
        maturity = min(1.0, max(0.0, self.maturity))
        return (1.0 - maturity) * max(0.0, self.blocker_score) * max(0.0, self.expected_value)


def choose_next_track(signals: Iterable[ResearchSignal]) -> ResearchSignal:
    valid = [signal for signal in signals if signal.track in RESEARCH_TRACKS]
    if not valid:
        raise ValueError("No valid research signals supplied")
    return max(valid, key=lambda signal: (signal.priority(), -RESEARCH_TRACKS.index(signal.track)))


def stage_complete(signal: ResearchSignal, plateau_count: int, tests_passed: bool) -> bool:
    return tests_passed and signal.maturity >= 0.90 and plateau_count >= 3
