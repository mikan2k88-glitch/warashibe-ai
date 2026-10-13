from dropship.fee_evidence import acquire_fee_evidence
from dropship.terms_evidence_acquisition import acquire_terms_evidence
from dropship.actual_evidence_controller_v66 import run_actual_evidence_controller_v66
from dropship.v66_proof import build_v66_proof, build_v66_acceptance
from dropship.v66_release import build_v66_release_status


def _candidate():
    return {
        "product_key": "p1",
        "name": "Product",
        "supplier": "proof",
        "supplier_cost": 8.0,
        "supplier_shipping": 4.5,
        "platform_fee_rate": 0.0,
        "payment_fee_rate": 0.0,
        "expected_return_cost": 0.0,
        "refund_reserve": 0.0,
        "delivery_days": 5,
        "inventory_confirmed": True,
        "supplier_reliable": True,
        "cost_evidence": {
            "supplier_cost": {"status": "known"},
            "supplier_shipping": {"status": "known"},
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
    }


class _FeeProvider:
    provider_name = "proof-fees"

    def fetch_fee_evidence(self, candidate):
        return {
            "status": "known",
            "platform_fee_rate": {
                "status": "known",
                "value": 0.10,
                "source": "official-marketplace-fee",
                "marketplace": "ebay-us",
            },
            "payment_fee_rate": {
                "status": "known",
                "value": 0.03,
                "source": "official-payment-fee",
                "marketplace": "ebay-us",
            },
            "expected_return_cost": {
                "status": "known",
                "value": 1.0,
                "source": "policy-model-v1",
            },
            "refund_reserve": {
                "status": "known",
                "value": 1.0,
                "source": "policy-model-v1",
            },
            "live_execution_allowed": False,
        }


class _UnknownFeeProvider:
    provider_name = "unknown-fees"

    def fetch_fee_evidence(self, candidate):
        return {
            "status": "unknown",
            "reason": "marketplace_credentials_pending",
            "live_execution_allowed": False,
        }


class _TermsProvider:
    provider_name = "proof-terms"

    def fetch_terms_evidence(self, candidate):
        return {
            "status": "known",
            "supplier_dropshipping_permission": {
                "status": "confirmed",
                "source": "supplier-terms",
            },
            "platform_terms": {
                "status": "confirmed",
                "source": "marketplace-policy",
            },
            "return_terms": {
                "status": "confirmed",
                "source": "marketplace-return-policy",
            },
            "cancellation_terms": {
                "status": "confirmed",
                "source": "marketplace-cancellation-policy",
            },
            "live_execution_allowed": False,
        }


class _UnknownTermsProvider:
    provider_name = "unknown-terms"

    def fetch_terms_evidence(self, candidate):
        return {
            "status": "unknown",
            "reason": "terms_not_verified",
            "live_execution_allowed": False,
        }


def test_v66_fee_evidence_only_confirms_sourced_values():
    result = acquire_fee_evidence(_candidate(), fee_provider=_FeeProvider())
    candidate = result["candidate"]
    assert result["status"] == "fee_evidence_acquired"
    assert candidate["platform_fee_rate"] == 0.10
    assert candidate["payment_fee_rate"] == 0.03
    assert candidate["expected_return_cost"] == 1.0
    assert candidate["refund_reserve"] == 1.0
    assert candidate["cost_evidence"]["platform_fee_rate"]["status"] == "known"
    assert candidate["cost_evidence"]["platform_fee_rate"]["marketplace"] == "ebay-us"
    assert result["live_execution_allowed"] is False


def test_v66_unknown_fee_evidence_keeps_fields_unknown():
    result = acquire_fee_evidence(_candidate(), fee_provider=_UnknownFeeProvider())
    candidate = result["candidate"]
    assert result["status"] == "fee_evidence_unavailable"
    assert candidate["cost_evidence"]["platform_fee_rate"]["status"] == "unknown"
    assert candidate["cost_evidence"]["payment_fee_rate"]["status"] == "unknown"


def test_v66_terms_evidence_requires_explicit_confirmation():
    result = acquire_terms_evidence(_candidate(), terms_provider=_TermsProvider())
    candidate = result["candidate"]
    assert result["status"] == "terms_evidence_acquired"
    assert candidate["terms_evidence"]["platform_terms"]["status"] == "confirmed"
    assert candidate["terms_evidence"]["return_terms"]["status"] == "confirmed"
    assert candidate["platform_terms_confirmed"] is True
    assert candidate["return_terms_confirmed"] is True
    assert result["live_execution_allowed"] is False


def test_v66_unknown_terms_remain_blocked():
    result = acquire_terms_evidence(_candidate(), terms_provider=_UnknownTermsProvider())
    candidate = result["candidate"]
    assert result["status"] == "terms_evidence_unavailable"
    assert candidate["terms_evidence"]["return_terms"]["status"] == "unknown"
    assert candidate.get("return_terms_confirmed") is not True


class _Supplier:
    provider_name = "proof-supplier"

    def fetch_offers(self):
        row = _candidate()
        row["supplier"] = self.provider_name
        return [row]


class _Freight:
    def fetch_shipping_evidence(self, candidate, *, destination_country, quantity):
        return {
            "status": "known",
            "source": "cj-freight-calculate",
            "shipping_cost": 4.5,
            "currency": "USD",
            "variant_id": "v1",
            "origin_country": "CN",
            "destination_country": destination_country,
            "quantity": quantity,
            "logistic_name": "Economy",
            "logistic_aging": "8-12",
            "live_execution_allowed": False,
        }


class _Market:
    provider_name = "ebay-browse"

    def search(self, query):
        return [
            {"price": 24, "currency": "USD", "seller_username": "a"},
            {"price": 25, "currency": "USD", "seller_username": "b"},
            {"price": 26, "currency": "USD", "seller_username": "c"},
            {"price": 25.5, "currency": "USD", "seller_username": "d"},
            {"price": 24.5, "currency": "USD", "seller_username": "e"},
            {"price": 26.5, "currency": "USD", "seller_username": "f"},
        ]


class _MemoryPersistence:
    def __init__(self):
        self.tables = {"dropship_observations": [], "dropship_research_runs": []}
        for day in range(1, 8):
            for idx in range(3):
                observation = {
                    "product_key": "p1",
                    "supplier": "proof-supplier",
                    "source": "real-read-opportunity",
                    "sale_price": 24 + idx * 0.5,
                    "supplier_cost": 8 + idx * 0.05,
                    "inventory_confirmed": True,
                    "expected_net_profit": 5 + idx,
                    "opportunity_score": 0.8,
                    "observed_at": f"2026-10-{day:02d}T0{idx}:00:00+00:00",
                }
                self.tables["dropship_observations"].append({
                    "product_key": observation["product_key"],
                    "supplier": observation["supplier"],
                    "source": observation["source"],
                    "observed_at": observation["observed_at"],
                    "observation_fingerprint": f"v66-{day}-{idx}",
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


def _run(fee_provider, terms_provider):
    return run_actual_evidence_controller_v66(
        _Supplier(),
        _Market(),
        freight_provider=_Freight(),
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


def test_v66_unknown_fee_blocks_human_gate():
    result = _run(_UnknownFeeProvider(), _TermsProvider())
    assert result["controller_version"] == "6.6"
    assert result["human_gate_ready_count"] == 0
    assert result["fee_evidence"]["unavailable_count"] == 1


def test_v66_unknown_return_terms_block_human_gate():
    result = _run(_FeeProvider(), _UnknownTermsProvider())
    assert result["human_gate_ready_count"] == 0
    assert result["terms_evidence"]["unavailable_count"] == 1


def test_v66_all_evidence_can_reach_human_gate():
    result = _run(_FeeProvider(), _TermsProvider())
    assert result["human_gate_ready_count"] == 1
    assert result["fee_evidence"]["acquired_count"] == 1
    assert result["terms_evidence"]["acquired_count"] == 1
    assert result["automatic_execution"] is False
    assert result["live_execution_allowed"] is False


def test_v66_proof_release_and_api():
    proof = build_v66_proof()
    acceptance = build_v66_acceptance()
    status = build_v66_release_status()
    assert proof["passed"] is True
    assert acceptance["passed"] is True
    assert status["status"] == "fee_terms_evidence_endpoint_reached"
    assert status["live_execution_allowed"] is False

    from app import app
    client = app.test_client()
    assert client.get("/dropship/v6.6/proof").status_code == 200
    assert client.get("/dropship/v6.6/acceptance").status_code == 200
    assert client.get("/dropship/v6.6/status").status_code == 200
