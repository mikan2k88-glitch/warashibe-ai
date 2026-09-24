"""Conflict-aware evidence grouping for cross-market observations.

A matching primary identity key is necessary but not sufficient: observations
are merged only when shared deterministic identifiers do not conflict.
"""

from collections import defaultdict
from typing import Iterable

from research_lab.identifier_conflict_resolution import assess_identity_conflicts
from research_lab.market_evidence_estimator import MarketEstimate, estimate_market
from research_lab.market_identity_resolution import identity_key
from research_lab.real_market_schema import MarketObservation

CONFLICT_GROUPING_VERSION = "0.1"


def group_conflict_aware(observations: Iterable[MarketObservation]) -> list[list[MarketObservation]]:
    buckets = defaultdict(list)
    for observation in observations:
        buckets[identity_key(observation)].append(observation)

    groups = []
    for _, rows in sorted(buckets.items()):
        safe_groups = []
        for row in rows:
            placed = False
            for group in safe_groups:
                if all(assess_identity_conflicts(row, other).safe_to_merge for other in group):
                    group.append(row)
                    placed = True
                    break
            if not placed:
                safe_groups.append([row])
        groups.extend(safe_groups)
    return groups


def estimate_conflict_aware(observations: Iterable[MarketObservation]) -> list[MarketEstimate]:
    return [estimate_market(group) for group in group_conflict_aware(observations)]
