from __future__ import annotations

from .actual_evidence_controller_v65 import run_actual_evidence_controller_v65
from .fee_evidence import acquire_fee_evidence
from .terms_evidence_acquisition import acquire_terms_evidence


class _FeeTermsSupplierWrapper:
    def __init__(self, supplier_provider, fee_provider, terms_provider):
        self.supplier_provider = supplier_provider
        self.fee_provider = fee_provider
        self.terms_provider = terms_provider
        self.provider_name = getattr(supplier_provider, "provider_name", "unknown")
        self.fee_stats = {"attempted_count": 0, "acquired_count": 0, "unavailable_count": 0}
        self.terms_stats = {"attempted_count": 0, "acquired_count": 0, "unavailable_count": 0}

    def fetch_offers(self) -> list[dict]:
        enriched = []
        for candidate in self.supplier_provider.fetch_offers():
            self.fee_stats["attempted_count"] += 1
            fee = acquire_fee_evidence(candidate, fee_provider=self.fee_provider)
            if fee["status"] == "fee_evidence_acquired":
                self.fee_stats["acquired_count"] += 1
            else:
                self.fee_stats["unavailable_count"] += 1

            self.terms_stats["attempted_count"] += 1
            terms = acquire_terms_evidence(
                fee["candidate"],
                terms_provider=self.terms_provider,
            )
            if terms["status"] == "terms_evidence_acquired":
                self.terms_stats["acquired_count"] += 1
            else:
                self.terms_stats["unavailable_count"] += 1

            enriched.append(terms["candidate"])
        return enriched


def run_actual_evidence_controller_v66(
    supplier_provider,
    market_provider,
    *,
    freight_provider,
    fee_provider,
    terms_provider,
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
    wrapper = _FeeTermsSupplierWrapper(
        supplier_provider,
        fee_provider,
        terms_provider,
    )
    base = run_actual_evidence_controller_v65(
        wrapper,
        market_provider,
        freight_provider=freight_provider,
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
        destination_country=destination_country,
        quantity=quantity,
        freight_max_items=freight_max_items,
    )
    return {
        **base,
        "controller_version": "6.6",
        "fee_evidence": {**wrapper.fee_stats, "read_only": True},
        "terms_evidence": {**wrapper.terms_stats, "read_only": True},
        "automatic_execution": False,
        "external_write_enabled": False,
        "live_execution_allowed": False,
    }
