from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderDescriptor:
    name: str
    mode: str = "read_only"
    supports_inventory: bool = True
    supports_price: bool = True
    supports_tracking: bool = False
    supports_orders: bool = False


class ProviderRegistry:
    def __init__(self):
        self._providers = {}

    def register(self, descriptor: ProviderDescriptor) -> None:
        if descriptor.mode != "read_only":
            raise ValueError("only read_only providers may be registered in research v1.x")
        if descriptor.supports_orders:
            raise ValueError("order-capable providers are not allowed in research v1.x")
        self._providers[descriptor.name] = descriptor

    def list(self) -> list[dict]:
        return [
            {
                "name": item.name,
                "mode": item.mode,
                "supports_inventory": item.supports_inventory,
                "supports_price": item.supports_price,
                "supports_tracking": item.supports_tracking,
                "supports_orders": item.supports_orders,
            }
            for item in sorted(self._providers.values(), key=lambda row: row.name)
        ]

    def get(self, name: str) -> dict | None:
        item = self._providers.get(name)
        if item is None:
            return None
        return {
            "name": item.name,
            "mode": item.mode,
            "supports_inventory": item.supports_inventory,
            "supports_price": item.supports_price,
            "supports_tracking": item.supports_tracking,
            "supports_orders": item.supports_orders,
        }
