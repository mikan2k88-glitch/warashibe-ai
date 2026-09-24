"""Group normalized market observations into conservative evidence sets."""

from collections import defaultdict
from typing import Iterable

from research_lab.market_evidence_estimator import MarketEstimate, estimate_market
from research_lab.real_market_schema import MarketObservation

GROUPING_VERSION = "0.1"


def evidence_key(observation: MarketObservation) -> tuple[str, str, str]:
    """Stable coarse key; no fuzzy identity is invented."""
    return (
        observation.name.strip().casefold(),
        observation.category.strip().casefold(),
        observation.currency.strip().upper(),
    )


def group_evidence(observations: Iterable[MarketObservation]) -> dict[tuple[str, str, str], list[MarketObservation]]:
    groups = defaultdict(list)
    for observation in observations:
        groups[evidence_key(observation)].append(observation)
    return dict(groups)


def estimate_groups(observations: Iterable[MarketObservation]) -> list[MarketEstimate]:
    """Aggregate only exact normalized keys; fuzzy/entity matching is a later layer."""
    groups = group_evidence(observations)
    return [estimate_market(rows) for _, rows in sorted(groups.items())]
