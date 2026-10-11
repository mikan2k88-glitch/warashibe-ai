from __future__ import annotations

from datetime import datetime, timezone


def build_outcome_record(payload: dict) -> dict:
    expected_profit = float(payload.get("expected_net_profit") or 0)
    realized_profit = float(payload.get("realized_net_profit") or expected_profit)
    return {
        "outcome_version": "1.0",
        "product_key": payload.get("product_key"),
        "supplier": payload.get("supplier"),
        "category": payload.get("category"),
        "strategy": payload.get("strategy"),
        "mode": str(payload.get("mode") or "sandbox"),
        "expected_net_profit": expected_profit,
        "realized_net_profit": realized_profit,
        "profit_error": round(realized_profit - expected_profit, 2),
        "delivered": payload.get("delivered") is True,
        "refunded": payload.get("refunded") is True,
        "delivery_days": int(payload.get("delivery_days") or 0),
        "observed_at": str(payload.get("observed_at") or datetime.now(timezone.utc).isoformat()),
        "live_transaction": False,
    }
