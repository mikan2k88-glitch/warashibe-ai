from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone


def _parse(value):
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)


def build_latest_candidates(observations: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for row in observations:
        key = str(row.get("product_key") or "unknown")
        groups[key].append(row)

    candidates = []
    for key, rows in groups.items():
        latest = max(rows, key=lambda row: _parse(row.get("observed_at")))
        candidates.append({
            **latest,
            "product_key": key,
            "observation_count": len(rows),
            "candidate_source": "latest_observation",
        })
    candidates.sort(key=lambda row: row["product_key"])
    return candidates
