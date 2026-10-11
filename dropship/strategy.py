from __future__ import annotations

SUPPORTED_DROPSHIP_STRATEGIES = {"safe", "balanced", "aggressive"}


def select_ranked_offer(ranking: dict, strategy: str = "balanced") -> dict | None:
    rows = list(ranking.get("ranked") or [])
    if not rows:
        return None
    strategy = strategy if strategy in SUPPORTED_DROPSHIP_STRATEGIES else "balanced"

    if strategy == "safe":
        return max(
            rows,
            key=lambda row: (
                float(row.get("supplier_score") or 0),
                float(row["economics"].get("margin") or 0),
                float(row["economics"].get("net_profit") or 0),
            ),
        )
    if strategy == "aggressive":
        return max(
            rows,
            key=lambda row: (
                float(row["economics"].get("net_profit") or 0),
                float(row.get("ranking_score") or 0),
            ),
        )
    return max(
        rows,
        key=lambda row: (
            float(row.get("ranking_score") or 0),
            float(row["economics"].get("net_profit") or 0),
        ),
    )
