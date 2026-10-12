from __future__ import annotations

import csv
import io

import requests

from .provider import ReadOnlySupplierProvider


class CsvFeedSupplierProvider(ReadOnlySupplierProvider):
    """GET-only CSV feed provider."""

    def __init__(
        self,
        url: str,
        *,
        provider_name: str = "csv-feed",
        headers: dict | None = None,
        timeout: int = 30,
        max_items: int = 500,
    ):
        self.url = url
        self.provider_name = provider_name
        self.headers = dict(headers or {})
        self.timeout = int(timeout)
        self.max_items = max(1, int(max_items))

    def fetch_offers(self) -> list[dict]:
        response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        reader = csv.DictReader(io.StringIO(response.text))
        return [
            {**dict(row), "source": dict(row).get("source") or self.provider_name}
            for _, row in zip(range(self.max_items), reader)
        ]
