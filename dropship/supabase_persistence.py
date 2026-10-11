from __future__ import annotations

from .observation_record import build_observation_record
from .run_record import build_research_run_record


OBSERVATION_TABLE = "dropship_observations"
RUN_TABLE = "dropship_research_runs"


def persist_observation(client, row: dict) -> dict:
    record = build_observation_record(row)
    return client.insert(OBSERVATION_TABLE, record)


def persist_observations(client, rows: list[dict]) -> dict:
    inserted = []
    duplicates = []
    errors = []

    for row in rows:
        record = build_observation_record(row)
        try:
            inserted.append(client.insert(OBSERVATION_TABLE, record))
        except Exception as exc:
            message = str(exc)
            if "23505" in message or "duplicate" in message.lower():
                duplicates.append(record["observation_fingerprint"])
            else:
                errors.append({
                    "product_key": record["product_key"],
                    "error": message,
                })

    return {
        "inserted_count": len(inserted),
        "duplicate_count": len(duplicates),
        "error_count": len(errors),
        "inserted": inserted,
        "duplicate_fingerprints": duplicates,
        "errors": errors,
        "commerce_write": False,
    }


def load_observation_history(
    client,
    *,
    product_key: str | None = None,
    limit: int = 1000,
) -> list[dict]:
    filters = {"product_key": product_key} if product_key else {}
    rows = client.select(
        OBSERVATION_TABLE,
        columns="product_key,supplier,source,observed_at,observation_fingerprint,observation",
        filters=filters,
        order="observed_at.desc",
        limit=limit,
    )
    history = []
    for row in rows:
        observation = dict(row.get("observation") or {})
        observation.setdefault("product_key", row.get("product_key"))
        observation.setdefault("supplier", row.get("supplier"))
        observation.setdefault("source", row.get("source"))
        observation.setdefault("observed_at", row.get("observed_at"))
        observation.setdefault("observation_fingerprint", row.get("observation_fingerprint"))
        history.append(observation)
    return history


def persist_run(client, result: dict, *, mode: str) -> dict:
    record = build_research_run_record(result, mode=mode)
    row = {
        "sha256": record["sha256"],
        "mode": record["mode"],
        "supplier_provider": record["supplier_provider"],
        "market_provider": record["market_provider"],
        "best_product_key": record["best_product_key"],
        "best_opportunity_score": record["best_opportunity_score"],
        "record": record,
        "observed_at": record["observed_at"],
    }
    return client.insert(RUN_TABLE, row)


def load_recent_runs(client, *, limit: int = 100) -> list[dict]:
    rows = client.select(
        RUN_TABLE,
        columns="sha256,mode,supplier_provider,market_provider,best_product_key,best_opportunity_score,record,observed_at",
        order="observed_at.desc",
        limit=limit,
    )
    return [dict(row.get("record") or row) for row in rows]
