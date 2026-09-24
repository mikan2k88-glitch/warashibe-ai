"""Read-only provider contract for live market evidence research.

A provider only discovers evidence. It must not buy, list, pay, mutate accounts,
or own credentials. Authentication/network clients remain injected outside this
contract so CI stays deterministic and secret-free.
"""

from typing import Any, Iterable, Protocol, runtime_checkable

PROVIDER_CONTRACT_VERSION = "0.1"


@runtime_checkable
class MarketEvidenceProvider(Protocol):
    """Minimal contract implemented by read-only market evidence providers."""

    @property
    def name(self) -> str:
        ...

    def fetch(self, query: str) -> Iterable[dict[str, Any]]:
        ...


def validate_provider(provider: object) -> list[str]:
    """Return contract errors without invoking the provider or external I/O."""
    errors = []
    name = getattr(provider, "name", None)
    if not isinstance(name, str) or not name.strip():
        errors.append("provider name is required")
    if not callable(getattr(provider, "fetch", None)):
        errors.append("provider fetch(query) is required")
    return errors


def fetch_provider_records(provider: MarketEvidenceProvider, query: str) -> tuple[str, list[dict[str, Any]]]:
    """Fetch one explicit query after validating the provider boundary."""
    errors = validate_provider(provider)
    if errors:
        raise ValueError("; ".join(errors))
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query is required")
    rows = list(provider.fetch(query.strip()))
    return provider.name.strip(), rows
