from __future__ import annotations

import requests

from .pagination import extract_items, next_page_url
from .provider import ReadOnlySupplierProvider
from .rate_limit import ReadRateLimiter


class PagedHttpJsonSupplierProvider(ReadOnlySupplierProvider):
    """Generic authenticated GET-only provider with bounded pagination."""

    def __init__(
        self,
        url: str,
        *,
        provider_name: str,
        headers: dict | None = None,
        timeout: int = 30,
        min_interval_seconds: float = 1.0,
        max_pages: int = 5,
        max_items: int = 500,
    ):
        self.url = url
        self.provider_name = provider_name
        self.headers = dict(headers or {})
        self.timeout = int(timeout)
        self.max_pages = max(1, int(max_pages))
        self.max_items = max(1, int(max_items))
        self.rate_limiter = ReadRateLimiter(min_interval_seconds)

    def fetch_offers(self) -> list[dict]:
        items = []
        url = self.url
        seen_urls = set()

        for _ in range(self.max_pages):
            if not url or url in seen_urls or len(items) >= self.max_items:
                break
            seen_urls.add(url)
            self.rate_limiter.wait()
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
            items.extend(extract_items(payload))
            url = next_page_url(payload, current_url=url)

        return [
            {**row, "source": row.get("source") or self.provider_name}
            for row in items[: self.max_items]
        ]
