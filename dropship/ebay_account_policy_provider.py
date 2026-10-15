from __future__ import annotations

import os

import requests


RETURN_POLICY_URL = "https://api.ebay.com/sell/account/v1/return_policy"
SELL_ACCOUNT_READONLY_SCOPE = "https://api.ebay.com/oauth/api_scope/sell.account.readonly"


def assess_ebay_user_oauth_readiness(*, user_token: str | None = None) -> dict:
    token = user_token or os.environ.get("EBAY_USER_ACCESS_TOKEN", "")
    ready = bool(str(token).strip())
    return {
        "status": "ready" if ready else "setup_required",
        "user_token_present": ready,
        "return_policy_read_ready": ready,
        "required_scope": SELL_ACCOUNT_READONLY_SCOPE,
        "secret_values_exposed": False,
        "live_execution_allowed": False,
    }


class EbayAccountPolicyProvider:
    provider_name = "ebay-account-policy-read-v67"

    def __init__(
        self,
        *,
        user_token: str | None = None,
        marketplace_id: str = "EBAY_US",
        timeout: int = 30,
        session=None,
    ):
        self.user_token = user_token or os.environ.get("EBAY_USER_ACCESS_TOKEN", "")
        self.marketplace_id = str(marketplace_id)
        self.timeout = int(timeout)
        self.session = session or requests

    def fetch_return_policy_evidence(self) -> dict:
        if not self.user_token:
            return {
                "status": "unknown",
                "reason": "ebay_user_access_token_required",
                "required_scope": SELL_ACCOUNT_READONLY_SCOPE,
                "marketplace": self.marketplace_id,
                "secret_values_exposed": False,
                "live_execution_allowed": False,
            }

        try:
            response = self.session.get(
                RETURN_POLICY_URL,
                headers={
                    "Authorization": f"Bearer {self.user_token}",
                    "Content-Type": "application/json",
                },
                params={"marketplace_id": self.marketplace_id},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            policies = [
                row for row in (payload.get("returnPolicies") or [])
                if isinstance(row, dict)
            ]
            if not policies:
                return {
                    "status": "unknown",
                    "reason": "no_return_policy_configured",
                    "required_scope": SELL_ACCOUNT_READONLY_SCOPE,
                    "marketplace": self.marketplace_id,
                    "secret_values_exposed": False,
                    "live_execution_allowed": False,
                }

            policy = policies[0]
            period = policy.get("returnPeriod") or {}
            days = period.get("value") if str(period.get("unit") or "").upper() == "DAY" else None

            return {
                "status": "known",
                "return_terms": {
                    "status": "confirmed",
                    "source": RETURN_POLICY_URL,
                    "source_kind": "seller_account_api",
                    "marketplace": self.marketplace_id,
                    "return_policy_id": policy.get("returnPolicyId"),
                    "return_policy_name": policy.get("name"),
                    "returns_accepted": policy.get("returnsAccepted"),
                    "return_period_days": days,
                    "return_shipping_cost_payer": policy.get("returnShippingCostPayer"),
                },
                "required_scope": SELL_ACCOUNT_READONLY_SCOPE,
                "secret_values_exposed": False,
                "live_execution_allowed": False,
            }
        except requests.HTTPError as exc:
            response = exc.response
            status_code = response.status_code if response is not None else None
            # Whitelist only non-sensitive numeric eBay error identifiers.
            error_ids = []
            if response is not None:
                try:
                    body = response.json()
                    if isinstance(body, dict):
                        for item in body.get("errors", [])[:5]:
                            if isinstance(item, dict) and isinstance(item.get("errorId"), int):
                                error_ids.append(item["errorId"])
                except (ValueError, TypeError, AttributeError):
                    pass
            return {
                "status": "unknown",
                "reason": "ebay_return_policy_http_error",
                "http_status": status_code,
                "ebay_error_ids": error_ids,
                "required_scope": SELL_ACCOUNT_READONLY_SCOPE,
                "marketplace": self.marketplace_id,
                "secret_values_exposed": False,
                "live_execution_allowed": False,
            }
        except Exception as exc:
            return {
                "status": "unknown",
                "reason": exc.__class__.__name__,
                "required_scope": SELL_ACCOUNT_READONLY_SCOPE,
                "marketplace": self.marketplace_id,
                "secret_values_exposed": False,
                "live_execution_allowed": False,
            }
