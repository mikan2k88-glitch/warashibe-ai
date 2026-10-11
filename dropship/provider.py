from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Iterable

import requests


class ReadOnlySupplierProvider(ABC):
    """Supplier discovery contract. Implementations must never mutate supplier state."""

    provider_name = "unknown"

    @abstractmethod
    def fetch_offers(self) -> list[dict]:
        raise NotImplementedError


class FixtureSupplierProvider(ReadOnlySupplierProvider):
    provider_name = "fixture"

    def __init__(self, offers: Iterable[dict]):
        self._offers = [dict(row) for row in offers]

    def fetch_offers(self) -> list[dict]:
        observed_at = datetime.now(timezone.utc).isoformat()
        return [
            {
                **row,
                "source": row.get("source") or self.provider_name,
                "observed_at": row.get("observed_at") or observed_at,
            }
            for row in self._offers
        ]


class HttpJsonSupplierProvider(ReadOnlySupplierProvider):
    """Generic JSON GET adapter for read-only supplier APIs.

    It deliberately supports GET only. Response may be a list or
    {"offers": [...]}.
    """

    def __init__(
        self,
        url: str,
        *,
        provider_name: str = "http-json",
        timeout: int = 30,
        headers: dict | None = None,
    ):
        self.url = url
        self.provider_name = provider_name
        self.timeout = timeout
        self.headers = dict(headers or {})

    def fetch_offers(self) -> list[dict]:
        response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict):
            payload = payload.get("offers", [])
        if not isinstance(payload, list):
            raise ValueError("supplier provider response must be a list or contain offers list")
        return [
            {
                **dict(row),
                "source": dict(row).get("source") or self.provider_name,
            }
            for row in payload
            if isinstance(row, dict)
        ]
