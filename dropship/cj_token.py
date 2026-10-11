from __future__ import annotations

import os
import time

import requests


GET_TOKEN_URL = "https://developers.cjdropshipping.com/api2.0/v1/authentication/getAccessToken"
REFRESH_TOKEN_URL = "https://developers.cjdropshipping.com/api2.0/v1/authentication/refreshAccessToken"


class CJAccessTokenProvider:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        refresh_token: str | None = None,
        timeout: int = 30,
        session=None,
    ):
        self.api_key = api_key or os.environ.get("CJ_API_KEY", "")
        self.refresh_token = refresh_token or os.environ.get("CJ_REFRESH_TOKEN", "")
        self.timeout = int(timeout)
        self.session = session or requests
        self._access_token = None
        self._expires_at = 0.0

    def configured(self) -> bool:
        return bool(self.api_key or self.refresh_token)

    def _request(self, url: str, body: dict) -> dict:
        response = self.session.post(
            url,
            headers={"Content-Type": "application/json"},
            json=body,
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("code") != 200 or not isinstance(payload.get("data"), dict):
            raise RuntimeError(
                f"CJ token request failed: code={payload.get('code')} message={payload.get('message')}"
            )
        return payload["data"]

    def get_token(self) -> str:
        if self._access_token and time.time() < self._expires_at - 60:
            return self._access_token
        if not self.configured():
            raise RuntimeError("CJ API key or refresh token is not configured")

        if self.refresh_token:
            try:
                data = self._request(
                    REFRESH_TOKEN_URL,
                    {"refreshToken": self.refresh_token},
                )
            except Exception:
                if not self.api_key:
                    raise
                data = self._request(GET_TOKEN_URL, {"apiKey": self.api_key})
        else:
            data = self._request(GET_TOKEN_URL, {"apiKey": self.api_key})

        token = str(data.get("accessToken") or "")
        if not token:
            raise RuntimeError("CJ token response missing accessToken")

        # The API returns explicit expiry timestamps, but parsing provider-specific
        # timezone formats is unnecessary for safe caching. Cache locally for one hour;
        # future calls can safely re-obtain the server-cached token.
        self._access_token = token
        self._expires_at = time.time() + 3600
        new_refresh = str(data.get("refreshToken") or "")
        if new_refresh:
            self.refresh_token = new_refresh
        return token

    def describe(self) -> dict:
        return {
            "api_key_configured": bool(self.api_key),
            "refresh_token_configured": bool(self.refresh_token),
            "cached_token_present": bool(self._access_token),
            "secret_values_exposed": False,
        }
