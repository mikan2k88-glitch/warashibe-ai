"""Detect conflicting deterministic product identifiers before evidence merging."""

from dataclasses import dataclass

from research_lab.identifier_validation import (
    is_valid_gtin, normalize_gtin, is_valid_isbn, normalize_isbn,
)
from research_lab.market_identity_resolution import normalize_identity_text
from research_lab.real_market_schema import MarketObservation

CONFLICT_VERSION = "0.1"


@dataclass(frozen=True)
class IdentityAssessment:
    safe_to_merge: bool
    conflicts: tuple[str, ...]


def _ids(observation: MarketObservation) -> dict[str, str]:
    metadata = observation.metadata or {}
    ids = {}
    for field in ("gtin", "ean", "upc"):
        value = metadata.get(field)
        if value not in (None, "") and is_valid_gtin(value):
            ids["gtin"] = normalize_gtin(value)
            break
    value = metadata.get("isbn")
    if value not in (None, "") and is_valid_isbn(value):
        ids["isbn"] = normalize_isbn(value)
    value = metadata.get("model_number")
    if value not in (None, ""):
        ids["model_number"] = normalize_identity_text(value)
    return ids


def assess_identity_conflicts(left: MarketObservation, right: MarketObservation) -> IdentityAssessment:
    """Fail closed when any shared deterministic identifier disagrees."""
    left_ids, right_ids = _ids(left), _ids(right)
    shared = sorted(set(left_ids) & set(right_ids))
    conflicts = tuple(key for key in shared if left_ids[key] != right_ids[key])
    return IdentityAssessment(safe_to_merge=bool(shared) and not conflicts, conflicts=conflicts)
