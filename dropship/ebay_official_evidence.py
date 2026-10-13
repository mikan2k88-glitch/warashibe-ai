from __future__ import annotations


EBAY_SELLING_FEES_URL = "https://www.ebay.com/help/selling/fees-credits-invoices/x?id=4822"
EBAY_DROPSHIPPING_POLICY_URL = "https://www.ebay.com/help/selling/posting-items/setting-shipping-options/drop-shipping?id=4176"
EBAY_CANCELLATION_DOC_URL = "https://developer.ebay.com/api-docs/user-guides/static/trading-user-guide/order-cancellations.html"
CJ_EBAY_DROPSHIPPING_URL = "https://blog.cjdropshipping.com/detail/1436262133607014401"


class EbayOfficialFeeEvidenceProvider:
    provider_name = "ebay-official-fee-policy-v67"

    def __init__(self, *, marketplace_id: str = "EBAY_US"):
        self.marketplace_id = str(marketplace_id)

    def fetch_fee_evidence(self, candidate: dict) -> dict:
        return {
            "status": "known",
            "platform_fee_rate": {
                "status": "unknown",
                "reason": "category_subscription_and_seller_status_specific",
                "source": EBAY_SELLING_FEES_URL,
                "source_kind": "official_policy",
                "marketplace": self.marketplace_id,
            },
            "payment_fee_rate": {
                "status": "known",
                "value": 0.0,
                "source": EBAY_SELLING_FEES_URL,
                "source_kind": "official_policy",
                "marketplace": self.marketplace_id,
                "interpretation": "no_separate_third_party_payment_processing_fee",
            },
            "expected_return_cost": {
                "status": "unknown",
                "reason": "seller_return_policy_and_return_reason_required",
                "source_kind": "official_policy",
                "marketplace": self.marketplace_id,
            },
            "refund_reserve": {
                "status": "unknown",
                "reason": "historical_return_rate_or_policy_model_required",
                "source_kind": "policy_model_required",
                "marketplace": self.marketplace_id,
            },
            "live_execution_allowed": False,
        }


class EbayOfficialTermsEvidenceProvider:
    provider_name = "ebay-official-terms-policy-v67"

    def __init__(
        self,
        *,
        marketplace_id: str = "EBAY_US",
        account_policy_provider=None,
    ):
        self.marketplace_id = str(marketplace_id)
        self.account_policy_provider = account_policy_provider

    def fetch_terms_evidence(self, candidate: dict) -> dict:
        supplier = str(candidate.get("supplier") or "").strip().lower()
        cj_supplier = supplier in {"cjdropshipping", "cj dropshipping", "cj"}

        result = {
            "status": "known",
            "supplier_dropshipping_permission": (
                {
                    "status": "confirmed",
                    "source": CJ_EBAY_DROPSHIPPING_URL,
                    "source_kind": "supplier_official_publication",
                    "supplier": "CJdropshipping",
                    "marketplace": self.marketplace_id,
                }
                if cj_supplier
                else {
                    "status": "unknown",
                    "reason": "supplier_specific_permission_not_verified",
                    "source_kind": "supplier_evidence_required",
                    "marketplace": self.marketplace_id,
                }
            ),
            "platform_terms": {
                "status": "confirmed",
                "source": EBAY_DROPSHIPPING_POLICY_URL,
                "source_kind": "official_policy",
                "marketplace": self.marketplace_id,
                "constraint": "wholesale_supplier_fulfillment_only",
            },
            "return_terms": {
                "status": "unknown",
                "reason": "seller_specific_return_policy_requires_user_oauth",
                "source_kind": "seller_account_policy_required",
                "marketplace": self.marketplace_id,
            },
            "cancellation_terms": {
                "status": "confirmed",
                "source": EBAY_CANCELLATION_DOC_URL,
                "source_kind": "official_policy",
                "marketplace": self.marketplace_id,
            },
            "live_execution_allowed": False,
        }

        if self.account_policy_provider is not None:
            account = self.account_policy_provider.fetch_return_policy_evidence()
            if account.get("status") == "known" and isinstance(account.get("return_terms"), dict):
                result["return_terms"] = dict(account["return_terms"])

        return result
