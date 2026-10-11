from __future__ import annotations


REQUIRED_FIELDS = (
    "product_key",
    "name",
    "supplier",
    "sale_price",
    "supplier_cost",
    "delivery_days",
)


def assess_data_quality(row: dict) -> dict:
    checks = {
        "product_key": str(row.get("product_key") or "") not in {"", "unknown"},
        "name": str(row.get("name") or "") not in {"", "unknown"},
        "supplier": str(row.get("supplier") or "") not in {"", "unknown"},
        "sale_price": float(row.get("sale_price") or 0) > 0,
        "supplier_cost": float(row.get("supplier_cost") or 0) > 0,
        "delivery_days": int(row.get("delivery_days") or 0) > 0,
        "inventory_known": row.get("inventory_confirmed") in {True, False},
        "observed_at": bool(row.get("observed_at")),
        "source": bool(row.get("source")),
    }
    score = round(sum(1 for value in checks.values() if value) / len(checks), 6)
    critical = all(checks[key] for key in REQUIRED_FIELDS)
    return {
        "score": score,
        "critical_fields_passed": critical,
        "checks": checks,
        "promotion_data_ready": critical and score >= 0.8,
    }


def filter_quality(rows: list[dict], *, min_score: float = 0.8) -> dict:
    passed = []
    blocked = []
    for row in rows:
        quality = assess_data_quality(row)
        enriched = {**row, "data_quality": quality}
        if quality["critical_fields_passed"] and quality["score"] >= float(min_score):
            passed.append(enriched)
        else:
            blocked.append(enriched)
    return {
        "passed": passed,
        "blocked": blocked,
        "passed_count": len(passed),
        "blocked_count": len(blocked),
    }
