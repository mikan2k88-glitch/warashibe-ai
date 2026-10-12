from __future__ import annotations

from .actual_evidence_controller_v64 import run_actual_evidence_controller_v64
from .v62_proof import _MemoryPersistence, _RealMarket, _handshake


class _CompleteSupplier:
    provider_name = "proof-complete-supplier"

    def fetch_offers(self):
        return [{
            "product_key": "real-v62-product",
            "name": "Complete Product",
            "supplier": "proof-complete-supplier",
            "category": "home",
            "supplier_cost": 8,
            "supplier_shipping": 2,
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
                "supplier_shipping": {"status": "known"},
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


class _IncompleteSupplier(_CompleteSupplier):
    provider_name = "proof-incomplete-supplier"

    def fetch_offers(self):
        row = dict(super().fetch_offers()[0])
        row["supplier"] = self.provider_name
        row["supplier_shipping"] = 0
        row["cost_evidence"] = dict(row["cost_evidence"])
        row["cost_evidence"]["supplier_shipping"] = {
            "status": "unknown",
            "source": "not_returned_by_supplier",
        }
        return [row]


def _run(provider):
    return run_actual_evidence_controller_v64(
        provider,
        _RealMarket(),
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


def build_v64_proof() -> dict:
    complete = _run(_CompleteSupplier())
    incomplete = _run(_IncompleteSupplier())
    incomplete_gate = incomplete["v64_promotion_gates"][0]

    checks = {
        "complete_candidate_reaches_human_gate": complete["human_gate_ready_count"] == 1,
        "incomplete_candidate_blocked": incomplete["human_gate_ready_count"] == 0,
        "unknown_shipping_detected": (
            "supplier_shipping"
            in incomplete_gate["cost_completeness"]["unknown_fields"]
        ),
        "terms_required": complete["v64_promotion_gates"][0]["terms_evidence"]["passed"] is True,
        "automatic_execution_disabled": complete["automatic_execution"] is False,
        "external_write_disabled": complete["external_write_enabled"] is False,
        "live_execution_disabled": complete["live_execution_allowed"] is False,
    }

    return {
        "proof_version": "6.4",
        "passed": all(checks.values()),
        "checks": checks,
        "complete_case": complete,
        "incomplete_case": incomplete,
        "maturity_ceiling": "cost_and_terms_evidence_human_gate",
        "live_execution_allowed": False,
    }


def build_v64_acceptance() -> dict:
    proof = build_v64_proof()
    return {
        "acceptance_version": "6.4",
        "passed": proof["passed"],
        "endpoint": "cost_completeness_gate_ready",
        "human_gate_required": True,
        "automatic_execution": False,
        "live_execution_allowed": False,
    }
