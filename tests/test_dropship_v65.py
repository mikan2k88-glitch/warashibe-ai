from dropship.cost_completeness import assess_cost_completeness
from dropship.cost_evidence_acquisition import acquire_cost_evidence
from dropship.cj_freight_provider import CJFreightEvidenceProvider


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
