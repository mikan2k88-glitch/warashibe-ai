from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json

from .supabase_persistence import persist_observations


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _hour_bucket(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(
        minute=0, second=0, microsecond=0
    ).isoformat()


def _snapshot_fingerprint(row: dict, bucket: str) -> str:
    stable = {
        "mode": "cj_supplier_read",
        "bucket": bucket,
        "product_key": str(row.get("product_key") or ""),
        "supplier": str(row.get("supplier") or ""),
        "supplier_cost": row.get("supplier_cost"),
        "inventory_confirmed": row.get("inventory_confirmed"),
        "delivery_days": row.get("delivery_days"),
    }
    raw = json.dumps(stable, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def prepare_cj_supplier_observation(row: dict, *, observed_at: datetime) -> dict:
    item = dict(row)
    bucket = _hour_bucket(observed_at)
    metadata = dict(item.get("metadata") or {})
    metadata.update({
        "evidence_mode": "cj_supplier_read",
        "market_evidence_available": False,
        "promotion_eligible": False,
        "observation_bucket": bucket,
    })
    item.update({
        "source": "cj-supplier-shadow",
        "observed_at": observed_at.astimezone(timezone.utc).isoformat(),
        "observation_fingerprint": _snapshot_fingerprint(item, bucket),
        "market_evidence_available": False,
        "promotion_eligible": False,
        "live_execution_allowed": False,
        "metadata": metadata,
    })
    return item


def run_cj_supplier_collection(
    supplier_provider,
    *,
    persistence_client,
    max_items: int = 20,
    observed_at: datetime | None = None,
) -> dict:
    if persistence_client is None:
        return {
            "status": "setup_required",
            "reason": "supabase_persistence_required",
            "mode": "cj_supplier_read",
            "live_execution_allowed": False,
            "commerce_external_writes": False,
        }

    now = observed_at or _utc_now()
    try:
        offers = list(supplier_provider.fetch_offers())[: max(1, int(max_items))]
    except Exception as exc:
        return {
            "status": "provider_read_failed",
            "reason": exc.__class__.__name__,
            "mode": "cj_supplier_read",
            "supplier_provider": getattr(supplier_provider, "provider_name", "unknown"),
            "live_execution_allowed": False,
            "commerce_external_writes": False,
            "secret_values_exposed": False,
        }

    observations = [
        prepare_cj_supplier_observation(row, observed_at=now)
        for row in offers
        if isinstance(row, dict)
    ]
    persistence = persist_observations(persistence_client, observations)

    return {
        "status": "collecting_cj_supplier_evidence",
        "mode": "cj_supplier_read",
        "supplier_provider": getattr(supplier_provider, "provider_name", "unknown"),
        "fetched_count": len(offers),
        "observation_count": len(observations),
        "inserted_count": persistence["inserted_count"],
        "duplicate_count": persistence["duplicate_count"],
        "error_count": persistence["error_count"],
        "market_evidence_available": False,
        "promotion_review_enabled": False,
        "human_gate_candidate_ready": False,
        "live_execution_allowed": False,
        "commerce_external_writes": False,
        "secret_values_exposed": False,
    }
