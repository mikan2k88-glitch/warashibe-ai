from __future__ import annotations

from .actual_evidence_controller import run_actual_evidence_controller


class _RealSupplier:
    provider_name = "cjdropshipping-list-v2"

    def fetch_offers(self):
        return [{
            "product_key": "real-v62-product",
            "name": "Real V62 Product",
            "supplier": "cjdropshipping-list-v2",
            "category": "home",
            "supplier_cost": 8,
            "supplier_shipping": 0,
            "platform_fee_rate": 0.10,
            "payment_fee_rate": 0.035,
            "ad_cost": 0,
            "expected_return_cost": 0,
            "refund_reserve": 0,
            "delivery_days": 5,
            "inventory_confirmed": True,
            "supplier_allows_dropshipping": True,
            "platform_terms_confirmed": True,
            "supplier_reliable": True,
        }]


class _RealMarket:
    provider_name = "ebay-browse"

    def search(self, query):
        return [
            {"price": 20, "currency": "USD", "seller_username": "a"},
            {"price": 21, "currency": "USD", "seller_username": "b"},
            {"price": 22, "currency": "USD", "seller_username": "c"},
            {"price": 21.5, "currency": "USD", "seller_username": "d"},
            {"price": 20.5, "currency": "USD", "seller_username": "e"},
            {"price": 22.5, "currency": "USD", "seller_username": "f"},
        ]


class _MemoryPersistence:
    def __init__(self):
        self.tables = {
            "dropship_observations": [],
            "dropship_research_runs": [],
        }
        for day in range(1, 8):
            for index in range(3):
                observation = {
                    "product_key": "real-v62-product",
                    "supplier": "cjdropshipping-list-v2",
                    "source": "real-read-opportunity",
                    "sale_price": 20 + index * 0.5,
                    "supplier_cost": 8 + index * 0.05,
                    "inventory_confirmed": True,
                    "expected_net_profit": 5 + index,
                    "opportunity_score": 0.8,
                    "observed_at": f"2026-10-{day:02d}T0{index}:00:00+00:00",
                }
                self.tables["dropship_observations"].append({
                    "product_key": observation["product_key"],
                    "supplier": observation["supplier"],
                    "source": observation["source"],
                    "observed_at": observation["observed_at"],
                    "observation_fingerprint": f"proof-{day}-{index}",
                    "observation": observation,
                })

    def insert(self, table, row):
        stored = {"id": len(self.tables.setdefault(table, [])) + 1, **dict(row)}
        self.tables[table].append(stored)
        return stored

    def select(self, table, **kwargs):
        return list(self.tables.get(table, []))


def _handshake():
    return {
        "status": "real_provider_handshake_ready",
        "successful_provider_count": 2,
    }


def build_v62_proof() -> dict:
    persistence = _MemoryPersistence()
    result = run_actual_evidence_controller(
        _RealSupplier(),
        _RealMarket(),
        persistence_client=persistence,
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

    no_persistence = run_actual_evidence_controller(
        _RealSupplier(),
        _RealMarket(),
        persistence_client=None,
        provider_handshake=_handshake(),
    )

    no_handshake = run_actual_evidence_controller(
        _RealSupplier(),
        _RealMarket(),
        persistence_client=_MemoryPersistence(),
        provider_handshake={"status": "real_provider_handshake_incomplete"},
    )

    checks = {
        "actual_controller_ready": result["status"] == "human_gate_candidate_ready",
        "one_human_gate_candidate": result["human_gate_ready_count"] == 1,
        "real_product_ranked": result["real_product_ranking"]["eligible_count"] == 1,
        "promotion_review_ready": result["promotion_queue"]["ready_count"] == 1,
        "real_evidence_gate_ready": result["real_evidence_gates"][0]["status"] == "real_evidence_human_gate_ready",
        "persistence_required": no_persistence["status"] == "setup_required",
        "handshake_required": no_handshake["status"] == "setup_required",
        "automatic_execution_disabled": result["automatic_execution"] is False,
        "external_write_disabled": result["external_write_enabled"] is False,
        "live_execution_disabled": result["live_execution_allowed"] is False,
    }

    return {
        "proof_version": "6.2",
        "passed": all(checks.values()),
        "checks": checks,
        "result": result,
        "no_persistence": no_persistence,
        "no_handshake": no_handshake,
        "maturity_ceiling": "actual_evidence_human_gate",
        "live_execution_allowed": False,
    }


def build_v62_acceptance() -> dict:
    proof = build_v62_proof()
    return {
        "acceptance_version": "6.2",
        "passed": proof["passed"],
        "endpoint": "actual_evidence_controller_ready",
        "human_gate_required": True,
        "automatic_execution": False,
        "live_execution_allowed": False,
    }
