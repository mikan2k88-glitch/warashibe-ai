from __future__ import annotations

import os

import requests


CJ_VARIANT_QUERY_URL = "https://developers.cjdropshipping.com/api2.0/v1/product/variant/query"
CJ_VARIANT_BY_VID_URL = "https://developers.cjdropshipping.com/api2.0/v1/product/variant/queryByVid"
CJ_FREIGHT_URL = "https://developers.cjdropshipping.com/api2.0/v1/logistic/freightCalculate"


def _number(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _quote_total(row: dict) -> float:
    if row.get("totalPostageFee") is not None:
        return max(0.0, _number(row.get("totalPostageFee")))
    return max(
        0.0,
        _number(row.get("logisticPrice"))
        + _number(row.get("taxesFee"))
        + _number(row.get("clearanceOperationFee"))
        + _number(row.get("tariff")),
    )


class CJFreightEvidenceProvider:
    provider_name = "cj-freight-calculate"

    def __init__(
        self,
        *,
        token: str | None = None,
        token_env: str = "CJ_ACCESS_TOKEN",
        timeout: int = 30,
        session=None,
    ):
        self.token = token or os.environ.get(token_env, "")
        self.timeout = int(timeout)
        self.session = session or requests

    @property
    def headers(self) -> dict:
        if not self.token:
            raise RuntimeError("CJ access token is not configured")
        return {
            "CJ-Access-Token": self.token,
            "Content-Type": "application/json",
        }

    def _get(self, url: str, params: dict) -> dict:
        response = self.session.get(
            url,
            headers=self.headers,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("code") != 200 or payload.get("result") is not True:
            raise RuntimeError("CJ read request failed")
        return payload

    def _post(self, url: str, body: dict) -> dict:
        response = self.session.post(
            url,
            headers=self.headers,
            json=body,
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("code") != 200 or payload.get("result") is not True:
            raise RuntimeError("CJ freight request failed")
        return payload

    def _select_variant(self, product_key: str) -> dict | None:
        payload = self._get(CJ_VARIANT_QUERY_URL, {"pid": product_key})
        rows = [row for row in (payload.get("data") or []) if isinstance(row, dict)]
        if not rows:
            return None
        rows.sort(
            key=lambda row: (
                _number(row.get("variantSellPrice")) <= 0,
                _number(row.get("variantSellPrice")),
                str(row.get("vid") or ""),
            )
        )
        return rows[0]

    def _select_origin(self, variant_id: str) -> str | None:
        payload = self._get(
            CJ_VARIANT_BY_VID_URL,
            {"vid": variant_id, "features": "enable_inventory"},
        )
        data = payload.get("data") or {}
        inventories = [
            row for row in (data.get("inventories") or [])
            if isinstance(row, dict)
            and _number(row.get("totalInventory")) > 0
            and row.get("countryCode")
        ]
        if not inventories:
            return None
        inventories.sort(
            key=lambda row: (
                -_number(row.get("totalInventory")),
                str(row.get("countryCode") or ""),
            )
        )
        return str(inventories[0]["countryCode"])

    def fetch_shipping_evidence(
        self,
        candidate: dict,
        *,
        destination_country: str = "US",
        quantity: int = 1,
    ) -> dict:
        try:
            product_key = str(candidate.get("product_key") or "")
            if not product_key:
                raise RuntimeError("product key missing")

            variant = self._select_variant(product_key)
            if not variant or not variant.get("vid"):
                return self._unknown("variant_not_found", destination_country)

            variant_id = str(variant["vid"])
            origin = self._select_origin(variant_id)
            if not origin:
                return self._unknown("inventory_origin_not_found", destination_country)

            payload = self._post(
                CJ_FREIGHT_URL,
                {
                    "startCountryCode": origin,
                    "endCountryCode": str(destination_country),
                    "products": [
                        {
                            "quantity": max(1, int(quantity)),
                            "vid": variant_id,
                        }
                    ],
                },
            )
            options = [row for row in (payload.get("data") or []) if isinstance(row, dict)]
            if not options:
                return self._unknown("no_shipping_option", destination_country)

            normalized = []
            for row in options:
                normalized.append({
                    "total": _quote_total(row),
                    "logistic_name": str(row.get("logisticName") or ""),
                    "logistic_aging": str(row.get("logisticAging") or ""),
                })
            normalized.sort(key=lambda row: (row["total"], row["logistic_name"]))
            best = normalized[0]

            return {
                "status": "known",
                "source": self.provider_name,
                "shipping_cost": round(best["total"], 2),
                "currency": "USD",
                "variant_id": variant_id,
                "variant_sell_price": _number(variant.get("variantSellPrice")) if _number(variant.get("variantSellPrice")) > 0 else None,
                "variant_price_source": "cj-variant-query",
                "origin_country": origin,
                "destination_country": str(destination_country),
                "quantity": max(1, int(quantity)),
                "logistic_name": best["logistic_name"],
                "logistic_aging": best["logistic_aging"],
                "option_count": len(normalized),
                "selection_basis": "lowest_total_postage_for_selected_variant",
                "commerce_external_writes": False,
                "live_execution_allowed": False,
                "secret_values_exposed": False,
            }
        except Exception as exc:
            return self._unknown(exc.__class__.__name__, destination_country)

    def _unknown(self, reason: str, destination_country: str) -> dict:
        return {
            "status": "unknown",
            "source": self.provider_name,
            "reason": str(reason),
            "destination_country": str(destination_country),
            "commerce_external_writes": False,
            "live_execution_allowed": False,
            "secret_values_exposed": False,
        }
