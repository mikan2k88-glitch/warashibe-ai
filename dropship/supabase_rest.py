from __future__ import annotations

import os

import requests


class SupabaseRestClient:
    """Minimal server-side PostgREST client for append-only research data."""

    def __init__(
        self,
        *,
        url: str | None = None,
        key: str | None = None,
        timeout: int = 30,
        session=None,
    ):
        self.url = (url or os.environ.get("SUPABASE_URL") or "").rstrip("/")
        self.key = key or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_KEY") or ""
        self.timeout = int(timeout)
        self.session = session or requests

        if not self.url:
            raise ValueError("SUPABASE_URL is required")
        if not self.key:
            raise ValueError("Supabase server secret/service-role key is required")

    @property
    def headers(self) -> dict:
        return {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }

    def insert(self, table: str, row: dict) -> dict:
        response = self.session.post(
            f"{self.url}/rest/v1/{table}",
            headers={**self.headers, "Prefer": "return=representation"},
            json=dict(row),
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list) or not payload:
            raise RuntimeError(f"{table} insert returned no row")
        return dict(payload[0])

    def select(
        self,
        table: str,
        *,
        columns: str = "*",
        filters: dict | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        params = {"select": columns}
        for key, value in (filters or {}).items():
            params[key] = f"eq.{value}"
        if order:
            params["order"] = order
        if limit is not None:
            params["limit"] = str(int(limit))

        response = self.session.get(
            f"{self.url}/rest/v1/{table}",
            headers=self.headers,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        return [dict(row) for row in payload] if isinstance(payload, list) else []
