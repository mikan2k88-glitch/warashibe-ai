from __future__ import annotations

import os


def build_read_only_auth_headers(
    *,
    token_env: str | None = None,
    api_key_env: str | None = None,
    api_key_header: str = "X-API-Key",
) -> dict:
    headers = {}
    if token_env:
        token = os.environ.get(token_env, "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"
    if api_key_env:
        api_key = os.environ.get(api_key_env, "").strip()
        if api_key:
            headers[api_key_header] = api_key
    return headers


def describe_auth_config(*, token_env: str | None = None, api_key_env: str | None = None) -> dict:
    return {
        "token_env": token_env,
        "api_key_env": api_key_env,
        "secrets_exposed": False,
        "mode": "read_only",
    }
