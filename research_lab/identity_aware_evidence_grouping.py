"""Group cross-market evidence only after conservative identity resolution."""

from collections import defaultdict
from typing import Iterable

from research_lab.market_evidence_estimator import MarketEstimate, estimate_market
from research_lab.market_identity_resolution import identity_key
from research_lab.real_market_schema import MarketObservation

IDENTITY_GROUPING_VERSION = "0.1"


def group_by_identity(
    observations: Iterable[MarketObservation],
) -> dict[tuple[str, str, str], list[MarketObservation]]:
    """Group observations sharing the same fail-closed identity key."""
    groups = defaultdict(list)
    for observation in observations:
        groups[identity_key(observation)].append(observation)
    return dict(groups)


def estimate_identity_groups(observations: Iterable[MarketObservation]) -> list[MarketEstimate]:
    """Estimate each resolved identity independently."""
    groups = group_by_identity(observations)
    return [estimate_market(rows) for _, rows in sorted(groups.items())]
