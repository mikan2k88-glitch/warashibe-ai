from __future__ import annotations


def build_promotion_queue(reviews: list[dict]) -> dict:
    ready = [row for row in reviews if row.get("eligible_for_human_review") is True]
    pending = [row for row in reviews if row.get("eligible_for_human_review") is not True]

    ready.sort(
        key=lambda row: (
            -float((row.get("summary") or {}).get("real_product_score") or 0),
            -float((row.get("summary") or {}).get("expected_net_profit") or 0),
            str(row.get("product_key") or ""),
        )
    )
    return {
        "status": "promotion_queue_ready",
        "ready_count": len(ready),
        "pending_count": len(pending),
        "next_review": ready[0] if ready else None,
        "ready": ready,
        "pending": pending,
        "human_gate_required": True,
        "automatic_promotion": False,
        "live_execution_allowed": False,
    }
