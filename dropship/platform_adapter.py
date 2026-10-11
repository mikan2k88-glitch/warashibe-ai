from __future__ import annotations

from abc import ABC, abstractmethod


class ReadOnlySalesChannelAdapter(ABC):
    """Sales-channel contract for research mode. No live listing methods."""

    channel_name = "unknown"

    @abstractmethod
    def build_listing_preview(self, candidate: dict) -> dict:
        raise NotImplementedError


class SandboxSalesChannelAdapter(ReadOnlySalesChannelAdapter):
    channel_name = "sandbox"

    def build_listing_preview(self, candidate: dict) -> dict:
        return {
            "channel": self.channel_name,
            "title": str(candidate.get("name") or "untitled"),
            "price": float(candidate.get("sale_price") or 0),
            "product_key": candidate.get("product_key"),
            "status": "preview_only",
            "external_write": False,
            "live_listing_created": False,
        }
