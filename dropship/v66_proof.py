from __future__ import annotations

from .actual_evidence_controller_v66 import run_actual_evidence_controller_v66
from .v65_proof import _KnownFreight
from .v62_proof import _MemoryPersistence, _RealMarket, _handshake


class _Supplier:
    provider_name = "proof-v66-supplier"

    def fetch_offers(self):
        return [{
            "product_key": "real-v62-product",
            "name": "V66 Product",
            "supplier": self.provider_name,
            "category": "home",
            "supplier_cost": 8,
            "supplier_shipping": 0,
            "platform_fee_rate": 0,
            "payment_fee_rate": 0,
            "expected_return_cost": 0,
            "refund_reserve": 0,
            "delivery_days": 5,
            "inventory_confirmed": True,
            "supplier_reliable": True,
            "cost_evidence": {
                "supplier_cost": {"status": "known"},
                "supplier_shipping": {"status": "unknown"},
                "platform_fee_rate": {"status": "unknown"},
                "payment_fee_rate": {"status": "unknown"},
                "expected_return_cost": {"status": "unknown"},
                "refund_reserve": {"status": "unknown"},
            },
            "terms_evidence": {
                "supplier_dropshipping_permission": {"status": "unknown"},
                "platform_terms": {"status": "unknown"},
                "return_terms": {"status": "unknown"},
                "cancellation_terms": {"status": "unknown"},
            },
        }]


class _FeeKnown:
    provider_name = "proof-fees"

    def fetch_fee_evidence(self, candidate):
        return {
            "status": "known",
            "platform_fee_rate": {"status": "known", "value": 0.10, "source": "official"},
            "payment_fee_rate": {"status": "known", "value": 0.03, "source": "official"},
            "expected_return_cost": {"status": "known", "value": 1.0, "source": "policy"},
            "refund_reserve": {"status": "known", "value": 1.0, "source": "policy"},
        }


class _FeeUnknown:
    provider_name = "proof-fees-pending"

    def fetch_fee_evidence(self, candidate):
        return {"status": "unknown", "reason": "pending"}


class _TermsKnown:
    provider_name = "proof-terms"

    def fetch_terms_evidence(self, candidate):
        return {
            "status": "known",
            "supplier_dropshipping_permission": {"status": "confirmed", "source": "supplier"},
            "platform_terms": {"status": "confirmed", "source": "marketplace"},
            "return_terms": {"status": "confirmed", "source": "return-policy"},
            "cancellation_terms": {"status": "confirmed", "source": "cancel-policy"},
        }


class _TermsUnknown:
    provider_name = "proof-terms-pending"

    def fetch_terms_evidence(self, candidate):
        return {"status": "unknown", "reason": "pending"}


def _run(fee_provider, terms_provider):
    return run_actual_evidence_controller_v66(
        _Supplier(),
        _RealMarket(),
        freight_provider=_KnownFreight(),
        fee_provider=fee_provider,
        terms_provider=terms_provider,
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
    )


def build_v66_proof() -> dict:
    complete = _run(_FeeKnown(), _TermsKnown())
    fee_unknown = _run(_FeeUnknown(), _TermsKnown())
    terms_unknown = _run(_FeeKnown(), _TermsUnknown())
    checks = {
        "complete_evidence_reaches_human_gate": complete["human_gate_ready_count"] == 1,
        "unknown_fee_blocks": fee_unknown["human_gate_ready_count"] == 0,
        "unknown_terms_block": terms_unknown["human_gate_ready_count"] == 0,
        "automatic_execution_disabled": complete["automatic_execution"] is False,
        "external_write_disabled": complete["external_write_enabled"] is False,
        "live_execution_disabled": complete["live_execution_allowed"] is False,
    }
    return {
        "proof_version": "6.6",
        "passed": all(checks.values()),
        "checks": checks,
        "complete_case": complete,
        "fee_unknown_case": fee_unknown,
        "terms_unknown_case": terms_unknown,
        "maturity_ceiling": "fee_terms_evidence_human_gate",
        "live_execution_allowed": False,
    }


def build_v66_acceptance() -> dict:
    proof = build_v66_proof()
    return {
        "acceptance_version": "6.6",
        "passed": proof["passed"],
        "endpoint": "fee_terms_evidence_ready",
        "human_gate_required": True,
        "automatic_execution": False,
        "live_execution_allowed": False,
    }
