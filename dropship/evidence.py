from __future__ import annotations

from datetime import datetime, timezone


def normalize_supplier_offer(payload: dict) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "product_key": str(payload.get("product_key") or payload.get("sku") or payload.get("name") or "unknown"),
        "name": str(payload.get("name") or "unknown"),
        "category": str(payload.get("category") or "general").lower(),
        "supplier": str(payload.get("supplier") or "unknown"),
        "source": str(payload.get("source") or "manual"),
        "source_url": payload.get("source_url"),
        "observed_at": str(payload.get("observed_at") or now),
        "sale_price": float(payload.get("sale_price") or 0),
        "supplier_cost": float(payload.get("supplier_cost") or 0),
        "supplier_shipping": float(payload.get("supplier_shipping") or 0),
        "delivery_days": int(payload.get("delivery_days") or 0),
        "supplier_allows_dropshipping": payload.get("supplier_allows_dropshipping") is True,
        "platform_terms_confirmed": payload.get("platform_terms_confirmed") is True,
        "supplier_reliable": payload.get("supplier_reliable") is True,
        "inventory_confirmed": payload.get("inventory_confirmed") is True,
        "metadata": dict(payload.get("metadata") or {}),
    }


def assess_evidence_integrity(offer: dict) -> dict:
    checks = {
        "product_key_present": offer.get("product_key") not in {None, "", "unknown"},
        "supplier_present": offer.get("supplier") not in {None, "", "unknown"},
        "source_present": bool(offer.get("source")),
        "sale_price_positive": float(offer.get("sale_price") or 0) > 0,
        "supplier_cost_positive": float(offer.get("supplier_cost") or 0) > 0,
        "delivery_days_known": int(offer.get("delivery_days") or 0) > 0,
    }
    passed = all(checks.values())
    return {
        "passed": passed,
        "checks": checks,
        "status": "passed" if passed else "blocked",
    }
