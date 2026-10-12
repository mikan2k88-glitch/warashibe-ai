from dropship.cost_completeness import assess_cost_completeness
from dropship.cost_evidence_acquisition import acquire_cost_evidence
from dropship.cj_freight_provider import CJFreightEvidenceProvider
from dropship.actual_evidence_controller_v65 import run_actual_evidence_controller_v65
from dropship.v65_proof import build_v65_proof, build_v65_acceptance
from dropship.v65_release import build_v65_release_status


class _Response:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"http {self.status_code}")

    def json(self):
        return self._payload


class _Session:
    def __init__(self):
        self.get_calls = []
        self.post_calls = []

    def get(self, url, headers, params, timeout):
        self.get_calls.append((url, params))
        if url.endswith("/product/variant/query"):
            return _Response({
                "code": 200,
                "result": True,
                "data": [
                    {"vid": "v2", "variantSellPrice": 8.5},
                    {"vid": "v1", "variantSellPrice": 8.0},
                ],
            })
        if url.endswith("/product/variant/queryByVid"):
            return _Response({
                "code": 200,
                "result": True,
                "data": {
                    "vid": params["vid"],
                    "inventories": [
                        {"countryCode": "CN", "totalInventory": 12},
                    ],
                },
            })
        raise AssertionError(url)

    def post(self, url, headers, json, timeout):
        self.post_calls.append((url, json))
        assert url.endswith("/logistic/freightCalculate")
        assert json == {
            "startCountryCode": "CN",
            "endCountryCode": "US",
            "products": [{"quantity": 1, "vid": "v1"}],
        }
        return _Response({
            "code": 200,
            "result": True,
            "data": [
                {
                    "logisticName": "Fast",
                    "logisticPrice": 5.0,
                    "taxesFee": 1.0,
                    "clearanceOperationFee": 0.5,
                    "totalPostageFee": 6.5,
                    "logisticAging": "5-8",
                },
                {
                    "logisticName": "Economy",
                    "logisticPrice": 4.0,
                    "taxesFee": 0.5,
                    "clearanceOperationFee": 0.0,
                    "totalPostageFee": 4.5,
                    "logisticAging": "8-12",
                },
            ],
        })


def _candidate():
    return {
        "product_key": "p1",
        "supplier_cost": 8.0,
        "supplier_shipping": 0.0,
        "platform_fee_rate": 0.10,
        "payment_fee_rate": 0.03,
        "expected_return_cost": 1.0,
        "refund_reserve": 1.0,
        "cost_evidence": {
            "supplier_cost": {"status": "known"},
            "supplier_shipping": {"status": "unknown"},
            "platform_fee_rate": {"status": "known"},
            "payment_fee_rate": {"status": "known"},
            "expected_return_cost": {"status": "known"},
            "refund_reserve": {"status": "known"},
        },
    }


def test_v65_freight_read_uses_variant_inventory_and_cheapest_total():
    session = _Session()
    provider = CJFreightEvidenceProvider(token="secret", session=session)
    evidence = provider.fetch_shipping_evidence(
        _candidate(),
        destination_country="US",
        quantity=1,
    )
    assert evidence["status"] == "known"
    assert evidence["shipping_cost"] == 4.5
    assert evidence["currency"] == "USD"
    assert evidence["variant_id"] == "v1"
    assert evidence["origin_country"] == "CN"
    assert evidence["destination_country"] == "US"
    assert evidence["logistic_name"] == "Economy"
    assert evidence["commerce_external_writes"] is False
    assert evidence["live_execution_allowed"] is False


def test_v65_acquisition_only_marks_shipping_known():
    session = _Session()
    provider = CJFreightEvidenceProvider(token="secret", session=session)
    result = acquire_cost_evidence(
        _candidate(),
        freight_provider=provider,
        destination_country="US",
        quantity=1,
    )
    enriched = result["candidate"]
    assert result["status"] == "shipping_evidence_acquired"
    assert enriched["supplier_shipping"] == 4.5
    assert enriched["cost_evidence"]["supplier_shipping"]["status"] == "known"
    assert enriched["cost_evidence"]["supplier_shipping"]["source"] == "cj-freight-calculate"
    assert enriched["cost_evidence"]["supplier_cost"]["status"] == "known"
    assert assess_cost_completeness(enriched)["passed"] is True
    assert result["commerce_external_writes"] is False
    assert result["live_execution_allowed"] is False


def test_v65_failed_freight_keeps_unknown():
    class _FailProvider:
        def fetch_shipping_evidence(self, candidate, *, destination_country, quantity):
            return {
                "status": "unknown",
                "reason": "no_shipping_option",
                "commerce_external_writes": False,
                "live_execution_allowed": False,
            }

    result = acquire_cost_evidence(
        _candidate(),
        freight_provider=_FailProvider(),
        destination_country="US",
        quantity=1,
    )
    assert result["status"] == "shipping_evidence_unavailable"
    assert result["candidate"]["cost_evidence"]["supplier_shipping"]["status"] == "unknown"
    assert result["candidate"]["supplier_shipping"] == 0.0


def test_v65_never_calls_order_or_payment_endpoints():
    session = _Session()
    provider = CJFreightEvidenceProvider(token="secret", session=session)
    provider.fetch_shipping_evidence(_candidate(), destination_country="US", quantity=1)
    urls = [u for u, _ in session.get_calls] + [u for u, _ in session.post_calls]
    assert all("/shopping/" not in u for u in urls)
    assert all("/listed/" not in u for u in urls)


class _SupplierWithUnknownShipping:
    provider_name = "proof-v65-supplier"

    def fetch_offers(self):
        row = _candidate()
        row.update({
            "name": "V65 Product",
            "supplier": self.provider_name,
            "category": "home",
            "delivery_days": 5,
            "inventory_confirmed": True,
            "supplier_allows_dropshipping": True,
            "platform_terms_confirmed": True,
            "return_terms_confirmed": True,
            "cancellation_terms_confirmed": True,
            "supplier_reliable": True,
            "terms_evidence": {
                "supplier_dropshipping_permission": {"status": "confirmed"},
                "platform_terms": {"status": "confirmed"},
                "return_terms": {"status": "confirmed"},
                "cancellation_terms": {"status": "confirmed"},
            },
        })
        return [row]


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


class _KnownFreight:
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
            "commerce_external_writes": False,
            "live_execution_allowed": False,
        }


class _MemoryPersistence:
    def __init__(self):
        self.tables = {
            "dropship_observations": [],
            "dropship_research_runs": [],
        }
        for day in range(1, 8):
            for index in range(3):
                observation = {
                    "product_key": "p1",
                    "supplier": "proof-v65-supplier",
                    "source": "real-read-opportunity",
                    "sale_price": 24 + index * 0.5,
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
                    "observation_fingerprint": f"v65-{day}-{index}",
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


def test_v65_controller_acquires_shipping_before_v64_gate():
    result = run_actual_evidence_controller_v65(
        _SupplierWithUnknownShipping(),
        _Market(),
        freight_provider=_KnownFreight(),
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
    assert result["controller_version"] == "6.5"
    assert result["freight_evidence"]["attempted_count"] == 1
    assert result["freight_evidence"]["acquired_count"] == 1
    assert result["human_gate_ready_count"] == 1
    assert result["live_execution_allowed"] is False


def test_v65_proof_acceptance_release_and_flask_endpoints():
    proof = build_v65_proof()
    acceptance = build_v65_acceptance()
    status = build_v65_release_status()
    assert proof["passed"] is True
    assert acceptance["passed"] is True
    assert status["status"] == "cost_evidence_acquisition_endpoint_reached"
    assert status["live_execution_allowed"] is False

    from app import app
    client = app.test_client()
    assert client.get("/dropship/v6.5/proof").status_code == 200
    assert client.get("/dropship/v6.5/acceptance").status_code == 200
    assert client.get("/dropship/v6.5/status").status_code == 200


def test_v65_variant_with_missing_price_is_not_preferred():
    class _MissingPriceSession(_Session):
        def get(self, url, headers, params, timeout):
            self.get_calls.append((url, params))
            if url.endswith("/product/variant/query"):
                return _Response({
                    "code": 200,
                    "result": True,
                    "data": [
                        {"vid": "missing-price", "variantSellPrice": None},
                        {"vid": "priced", "variantSellPrice": 8.0},
                    ],
                })
            if url.endswith("/product/variant/queryByVid"):
                assert params["vid"] == "priced"
                return _Response({
                    "code": 200,
                    "result": True,
                    "data": {
                        "vid": "priced",
                        "inventories": [
                            {"countryCode": "CN", "totalInventory": 10},
                        ],
                    },
                })
            raise AssertionError(url)

        def post(self, url, headers, json, timeout):
            assert json["products"][0]["vid"] == "priced"
            return _Response({
                "code": 200,
                "result": True,
                "data": [{"logisticName": "Economy", "totalPostageFee": 3.0}],
            })

    provider = CJFreightEvidenceProvider(token="secret", session=_MissingPriceSession())
    evidence = provider.fetch_shipping_evidence(
        _candidate(),
        destination_country="US",
        quantity=1,
    )
    assert evidence["status"] == "known"
    assert evidence["variant_id"] == "priced"


def test_v65_controller_caps_freight_acquisition_to_one_by_default():
    class _TwoOfferSupplier(_SupplierWithUnknownShipping):
        def fetch_offers(self):
            first = super().fetch_offers()[0]
            second = dict(first)
            second["product_key"] = "p2"
            second["name"] = "V65 Product 2"
            return [first, second]

    class _CountingFreight(_KnownFreight):
        def __init__(self):
            self.calls = 0

        def fetch_shipping_evidence(self, candidate, *, destination_country, quantity):
            self.calls += 1
            return super().fetch_shipping_evidence(
                candidate,
                destination_country=destination_country,
                quantity=quantity,
            )

    freight = _CountingFreight()
    result = run_actual_evidence_controller_v65(
        _TwoOfferSupplier(),
        _Market(),
        freight_provider=freight,
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
    assert freight.calls == 1
    assert result["freight_evidence"]["attempted_count"] == 1
