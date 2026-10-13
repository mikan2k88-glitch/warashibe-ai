from dropship.ebay_official_evidence import (
    EbayOfficialFeeEvidenceProvider,
    EbayOfficialTermsEvidenceProvider,
)
from dropship.ebay_account_policy_provider import (
    EbayAccountPolicyProvider,
    assess_ebay_user_oauth_readiness,
)
from dropship.fee_evidence import acquire_fee_evidence
from dropship.terms_evidence_acquisition import acquire_terms_evidence


def _candidate():
    return {
        "product_key": "p1",
        "supplier": "CJdropshipping",
        "category": "general",
        "supplier_cost": 8.0,
        "supplier_shipping": 4.5,
        "platform_fee_rate": 0.0,
        "payment_fee_rate": 0.0,
        "expected_return_cost": 0.0,
        "refund_reserve": 0.0,
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


def test_v67_official_fee_evidence_only_confirms_separate_payment_fee():
    provider = EbayOfficialFeeEvidenceProvider(marketplace_id="EBAY_US")
    result = acquire_fee_evidence(_candidate(), fee_provider=provider)
    candidate = result["candidate"]

    assert candidate["payment_fee_rate"] == 0.0
    assert candidate["cost_evidence"]["payment_fee_rate"]["status"] == "known"
    assert candidate["cost_evidence"]["payment_fee_rate"]["source_kind"] == "official_policy"

    assert candidate["cost_evidence"]["platform_fee_rate"]["status"] == "unknown"
    assert candidate["cost_evidence"]["expected_return_cost"]["status"] == "unknown"
    assert candidate["cost_evidence"]["refund_reserve"]["status"] == "unknown"


def test_v67_official_terms_confirms_marketplace_supplier_and_cancellation_only():
    provider = EbayOfficialTermsEvidenceProvider(marketplace_id="EBAY_US")
    result = acquire_terms_evidence(_candidate(), terms_provider=provider)
    candidate = result["candidate"]

    assert candidate["terms_evidence"]["supplier_dropshipping_permission"]["status"] == "confirmed"
    assert candidate["terms_evidence"]["platform_terms"]["status"] == "confirmed"
    assert candidate["terms_evidence"]["cancellation_terms"]["status"] == "confirmed"

    assert candidate["terms_evidence"]["return_terms"]["status"] == "unknown"
    assert candidate["return_terms_confirmed"] is False


def test_v67_non_cj_supplier_does_not_get_supplier_permission_confirmation():
    candidate = _candidate()
    candidate["supplier"] = "unknown-retailer"
    provider = EbayOfficialTermsEvidenceProvider(marketplace_id="EBAY_US")
    result = acquire_terms_evidence(candidate, terms_provider=provider)
    assert result["candidate"]["terms_evidence"]["supplier_dropshipping_permission"]["status"] == "unknown"


def test_v67_user_oauth_readiness_fails_closed_without_user_token(monkeypatch):
    monkeypatch.delenv("EBAY_USER_ACCESS_TOKEN", raising=False)
    result = assess_ebay_user_oauth_readiness()
    assert result["status"] == "setup_required"
    assert result["user_token_present"] is False
    assert result["return_policy_read_ready"] is False
    assert result["live_execution_allowed"] is False


class _Response:
    status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return {
            "returnPolicies": [
                {
                    "returnPolicyId": "rp1",
                    "name": "30 day returns",
                    "marketplaceId": "EBAY_US",
                    "returnsAccepted": True,
                    "returnPeriod": {"value": 30, "unit": "DAY"},
                    "returnShippingCostPayer": "BUYER",
                }
            ]
        }


class _Session:
    def __init__(self):
        self.calls = []

    def get(self, url, headers, params, timeout):
        self.calls.append((url, headers, params))
        return _Response()


def test_v67_account_policy_provider_reads_return_policy_with_user_token():
    session = _Session()
    provider = EbayAccountPolicyProvider(
        user_token="user-token",
        marketplace_id="EBAY_US",
        session=session,
    )
    result = provider.fetch_return_policy_evidence()
    assert result["status"] == "known"
    assert result["return_terms"]["status"] == "confirmed"
    assert result["return_terms"]["returns_accepted"] is True
    assert result["return_terms"]["return_period_days"] == 30
    assert result["return_terms"]["return_shipping_cost_payer"] == "BUYER"
    assert result["live_execution_allowed"] is False
    assert "user-token" not in str(result)


def test_v67_account_policy_provider_uses_sell_account_scope_semantics():
    provider = EbayAccountPolicyProvider(user_token="", marketplace_id="EBAY_US")
    result = provider.fetch_return_policy_evidence()
    assert result["status"] == "unknown"
    assert result["reason"] == "ebay_user_access_token_required"
    assert result["required_scope"] == "https://api.ebay.com/oauth/api_scope/sell.account.readonly"
