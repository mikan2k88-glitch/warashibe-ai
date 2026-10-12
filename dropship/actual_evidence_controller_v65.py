from __future__ import annotations

from .actual_evidence_controller_v64 import run_actual_evidence_controller_v64
from .cost_evidence_acquisition import acquire_cost_evidence


class _CostEvidenceSupplierWrapper:
    def __init__(
        self,
        supplier_provider,
        freight_provider,
        *,
        destination_country: str,
        quantity: int,
        max_items: int,
    ):
        self.supplier_provider = supplier_provider
        self.freight_provider = freight_provider
        self.provider_name = getattr(supplier_provider, "provider_name", "unknown")
        self.destination_country = str(destination_country)
        self.quantity = max(1, int(quantity))
        self.max_items = max(1, int(max_items))
        self.stats = {
            "attempted_count": 0,
            "acquired_count": 0,
            "unavailable_count": 0,
        }

    def fetch_offers(self) -> list[dict]:
        offers = list(self.supplier_provider.fetch_offers())
        enriched = []
        for index, candidate in enumerate(offers):
            if index >= self.max_items:
                enriched.append(candidate)
                continue
            self.stats["attempted_count"] += 1
            result = acquire_cost_evidence(
                candidate,
                freight_provider=self.freight_provider,
                destination_country=self.destination_country,
                quantity=self.quantity,
            )
            if result["status"] == "shipping_evidence_acquired":
                self.stats["acquired_count"] += 1
            else:
                self.stats["unavailable_count"] += 1
            enriched.append(result["candidate"])
        return enriched


def run_actual_evidence_controller_v65(
    supplier_provider,
    market_provider,
    *,
    freight_provider,
    persistence_client,
    provider_handshake: dict,
    available_capital: float = 3000,
    supplier_currency: str = "USD",
    target_currency: str | None = None,
    fx_rates: dict | None = None,
    budget: dict | None = None,
    shadow_thresholds: dict | None = None,
    history_limit: int = 2000,
    run_limit: int = 200,
    destination_country: str = "US",
    quantity: int = 1,
    freight_max_items: int = 1,
) -> dict:
    limits = dict(budget or {})
    wrapper = _CostEvidenceSupplierWrapper(
        supplier_provider,
        freight_provider,
        destination_country=destination_country,
        quantity=quantity,
        max_items=min(
            int(limits.get("max_supplier_items") or 5),
            max(1, int(freight_max_items)),
        ),
    )

    base = run_actual_evidence_controller_v64(
        wrapper,
        market_provider,
        persistence_client=persistence_client,
        provider_handshake=provider_handshake,
        available_capital=available_capital,
        supplier_currency=supplier_currency,
        target_currency=target_currency,
        fx_rates=fx_rates,
        budget=budget,
        shadow_thresholds=shadow_thresholds,
        history_limit=history_limit,
        run_limit=run_limit,
    )

    return {
        **base,
        "controller_version": "6.5",
        "freight_evidence": {
            **wrapper.stats,
            "destination_country": str(destination_country),
            "quantity": max(1, int(quantity)),
            "read_only": True,
            "max_items": max(1, int(freight_max_items)),
        },
        "automatic_execution": False,
        "external_write_enabled": False,
        "live_execution_allowed": False,
    }
