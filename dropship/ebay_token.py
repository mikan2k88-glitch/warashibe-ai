from __future__ import annotations

import base64
import os
import time

import requests


PROD_TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
SANDBOX_TOKEN_URL = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
DEFAULT_SCOPE = "https://api.ebay.com/oauth/api_scope"


class EbayApplicationTokenProvider:
    def __init__(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        environment: str = "production",
        scope: str = DEFAULT_SCOPE,
        timeout: int = 30,
        session=None,
    ):
        self.client_id = client_id or os.environ.get("EBAY_CLIENT_ID", "")
        self.client_secret = client_secret or os.environ.get("EBAY_CLIENT_SECRET", "")
        self.environment = environment
        self.scope = scope
        self.timeout = int(timeout)
        self.session = session or requests
        self._access_token = None
        self._expires_at = 0.0

    def _token_url(self) -> str:
        return SANDBOX_TOKEN_URL if self.environment == "sandbox" else PROD_TOKEN_URL

    def configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def get_token(self) -> str:
        if self._access_token and time.time() < self._expires_at - 60:
            return self._access_token
        if not self.configured():
            raise RuntimeError("eBay client credentials are not configured")

        raw = f"{self.client_id}:{self.client_secret}".encode("utf-8")
        basic = base64.b64encode(raw).decode("ascii")
        response = self.session.post(
            self._token_url(),
            headers={
                "Authorization": f"Basic {basic}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "client_credentials",
                "scope": self.scope,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        token = str(payload.get("access_token") or "")
        expires_in = int(payload.get("expires_in") or 0)
        if not token or expires_in <= 0:
            raise RuntimeError("eBay token response missing access_token or expires_in")

        self._access_token = token
        self._expires_at = time.time() + expires_in
        return token

    def describe(self) -> dict:
        return {
            "configured": self.configured(),
            "environment": self.environment,
            "scope": self.scope,
            "cached_token_present": bool(self._access_token),
            "secret_values_exposed": False,
        }
