"""Storage abstraction for observed sale outcomes.

Research code depends on this small interface instead of a concrete JSON or
future remote backend.  Implementations must never fabricate observations.
"""

from typing import Protocol

from research_lab.raw_outcome_calibration import SaleOutcome


class OutcomeRepository(Protocol):
    def load(self) -> list[SaleOutcome]: ...

    def append(self, outcome: SaleOutcome) -> int: ...

    def for_opportunity(self, opportunity_key: str) -> list[SaleOutcome]: ...

    def stats(self) -> dict: ...


def validate_repository(repository: OutcomeRepository) -> OutcomeRepository:
    """Fail early when a backend does not satisfy the learning-loop contract."""
    required = ("load", "append", "for_opportunity", "stats")
    missing = [name for name in required if not callable(getattr(repository, name, None))]
    if missing:
        raise TypeError(f"Outcome repository missing methods: {', '.join(missing)}")
    return repository
