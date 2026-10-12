from __future__ import annotations

from .actual_evidence_controller_v65 import run_actual_evidence_controller_v65
from .v62_proof import _MemoryPersistence, _RealMarket, _handshake


class _Supplier:
    provider_name = "cjdropshipping-list-v2"

    def fetch_offers(self):
        return [{
            "product_key": "real-v62-product",
            "name": "V65 Product",
            "supplier": "cjdropshipping-list-v2",
            "category": "home",
            "supplier_cost": 8,
            "supplier_shipping": 0,
            "platform_fee_rate": 0.10,
            "payment_fee_rate": 0.035,
            "ad_cost": 0,
            "expected_return_cost": 1,
            "refund_reserve": 1,
            "delivery_days": 5,
            "inventory_confirmed": True,
            "supplier_allows_dropshipping": True,
            "platform_terms_confirmed": True,
            "return_terms_confirmed": True,
            "cancellation_terms_confirmed": True,
            "supplier_reliable": True,
            "cost_evidence": {
                "supplier_cost": {"status": "known"},
                "supplier_shipping": {"status": "unknown"},
                "platform_fee_rate": {"status": "known"},
                "payment_fee_rate": {"status": "known"},
                "expected_return_cost": {"status": "known"},
                "refund_reserve": {"status": "known"},
            },
            "terms_evidence": {
                "supplier_dropshipping_permission": {"status": "confirmed"},
                "platform_terms": {"status": "confirmed"},
                "return_terms": {"status": "confirmed"},
                "cancellation_terms": {"status": "confirmed"},
            },
        }]


class _KnownFreight:
    def fetch_shipping_evidence(self, candidate, *, destination_country, quantity):
        return {
            "status": "known",
            "source": "cj-freight-calculate",
            "shipping_cost": 4.5,
            "currency": "USD",
            "variant_id": "proof-vid",
            "origin_country": "CN",
            "destination_country": destination_country,
            "quantity": quantity,
            "logistic_name": "Proof Economy",
            "logistic_aging": "8-12",
            "commerce_external_writes": False,
            "live_execution_allowed": False,
        }


class _UnknownFreight:
    def fetch_shipping_evidence(self, candidate, *, destination_country, quantity):
        return {
            "status": "unknown",
            "source": "cj-freight-calculate",
            "reason": "no_shipping_option",
            "destination_country": destination_country,
            "commerce_external_writes": False,
            "live_execution_allowed": False,
        }


def _run(freight_provider):
    return run_actual_evidence_controller_v65(
        _Supplier(),
        _RealMarket(),
        freight_provider=freight_provider,
        persistence_client=_MemoryPersistence(),
        provider_handshake=_handshake(),
        available_capital=3000,
        supplier_currency="USD",
        target_currency="USD",
        budget={
            "max_supplier_items": 5,
            "max_market_queries": 5,
            "max_market_quotes_per_query": 10,
        },
        shadow_thresholds={
            "min_observations": 20,
            "min_observation_days": 7,
        },
        destination_country="US",
        quantity=1,
    )


def build_v65_proof() -> dict:
    known = _run(_KnownFreight())
    unknown = _run(_UnknownFreight())
    checks = {
        "shipping_evidence_acquired": known["freight_evidence"]["acquired_count"] == 1,
        "known_shipping_can_reach_gate": known["human_gate_ready_count"] == 1,
        "unknown_shipping_remains_blocked": unknown["human_gate_ready_count"] == 0,
        "read_only": known["freight_evidence"]["read_only"] is True,
        "automatic_execution_disabled": known["automatic_execution"] is False,
        "external_write_disabled": known["external_write_enabled"] is False,
        "live_execution_disabled": known["live_execution_allowed"] is False,
    }
    return {
        "proof_version": "6.5",
        "passed": all(checks.values()),
        "checks": checks,
        "known_case": known,
        "unknown_case": unknown,
        "maturity_ceiling": "cost_evidence_acquisition_human_gate",
        "live_execution_allowed": False,
    }


def build_v65_acceptance() -> dict:
    proof = build_v65_proof()
    return {
        "acceptance_version": "6.5",
        "passed": proof["passed"],
        "endpoint": "cost_evidence_acquisition_ready",
        "human_gate_required": True,
        "automatic_execution": False,
        "live_execution_allowed": False,
    }
