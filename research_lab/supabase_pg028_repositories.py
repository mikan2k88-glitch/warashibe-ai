"""Supabase append-only repositories for PG-028 Human Final Buy and execution audit."""

FINAL_BUY_TABLE = "warashibe_human_final_buy_confirmations"
EXECUTION_TABLE = "warashibe_single_purchase_executions"


class SupabaseHumanFinalBuyRepository:
    def __init__(self, client, table=FINAL_BUY_TABLE):
        if client is None:
            raise ValueError("client is required")
        self.client = client
        self.table = table

    def get(self, confirmation_key):
        response = (
            self.client.table(self.table)
            .select("confirmation_key,provider,item_key,decision,confirmation,confirmed_at,expires_at")
            .eq("confirmation_key", confirmation_key)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return dict(rows[0]) if rows else None

    def append(self, confirmation):
        if not isinstance(confirmation, dict):
            raise ValueError("confirmation must be a mapping")
        if confirmation.get("status") != "human_final_buy_recorded":
            raise ValueError("human_final_buy_recorded required")
        if confirmation.get("decision") not in {"buy", "do_not_buy"}:
            raise ValueError("invalid final buy decision")
        key = confirmation.get("confirmation_key")
        if not isinstance(key, str) or not key.strip():
            raise ValueError("confirmation_key is required")
        if self.get(key) is not None:
            raise ValueError("confirmation_key already exists")
        payload = {
            "confirmation_key": key,
            "provider": confirmation.get("provider"),
            "item_key": confirmation.get("item_key"),
            "decision": confirmation.get("decision"),
            "confirmation": dict(confirmation),
            "confirmed_at": confirmation.get("confirmed_at"),
            "expires_at": confirmation.get("expires_at"),
        }
        response = self.client.table(self.table).insert(payload).execute()
        rows = response.data or []
        if not rows:
            raise RuntimeError("Human Final Buy insert returned no row")
        return dict(rows[0])


class SupabaseSinglePurchaseExecutionRepository:
    def __init__(self, client, table=EXECUTION_TABLE):
        if client is None:
            raise ValueError("client is required")
        self.client = client
        self.table = table

    def get_by_idempotency_key(self, key):
        if not isinstance(key, str) or not key.strip():
            raise ValueError("idempotency key is required")
        response = (
            self.client.table(self.table)
            .select("idempotency_key,confirmation_key,provider,item_key,result,executed_at")
            .eq("idempotency_key", key.strip())
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return dict(rows[0]) if rows else None

    def append(self, row):
        if not isinstance(row, dict):
            raise ValueError("execution row must be a mapping")
        required = (
            "idempotency_key",
            "confirmation_key",
            "provider",
            "item_key",
            "result",
            "executed_at",
        )
        missing = [key for key in required if key not in row]
        if missing:
            raise ValueError("execution row missing keys: " + ",".join(missing))
        result = row["result"]
        if not isinstance(result, dict) or result.get("status") != "single_purchase_executed":
            raise ValueError("single_purchase_executed result required")
        if result.get("execution_count") != 1:
            raise ValueError("execution_count must be one")
        if self.get_by_idempotency_key(row["idempotency_key"]) is not None:
            raise ValueError("idempotency key already exists")
        response = self.client.table(self.table).insert({
            "idempotency_key": row["idempotency_key"],
            "confirmation_key": row["confirmation_key"],
            "provider": row["provider"],
            "item_key": row["item_key"],
            "result": dict(result),
            "executed_at": row["executed_at"],
        }).execute()
        rows = response.data or []
        if not rows:
            raise RuntimeError("single purchase execution insert returned no row")
        return dict(rows[0])
