"""Supabase append-only audit repository for PG-023 sandbox commerce attempts."""

TABLE_NAME = "warashibe_sandbox_commerce_attempts"


class SupabaseSandboxCommerceAttemptRepository:
    def __init__(self, client, table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client = client
        self.table = table

    @staticmethod
    def _validate(attempt):
        if not isinstance(attempt, dict):
            raise ValueError("attempt must be a mapping")
        required = ("attempt_key","intent_key","provider","requested_action","result","attempted_at")
        missing=[key for key in required if key not in attempt]
        if missing:
            raise ValueError("attempt missing required keys: "+",".join(missing))
        result=attempt["result"]
        if not isinstance(result, dict) or result.get("status")!="sandbox_blocked":
            raise ValueError("sandbox_blocked result required")
        if result.get("adapter_mode")!="sandbox_noop":
            raise ValueError("sandbox_noop mode required")
        if result.get("network_call_attempted") is not False:
            raise ValueError("network calls must remain disabled")
        if result.get("external_write_attempted") is not False:
            raise ValueError("external writes must remain disabled")
        for key in ("commerce_authorized","external_action_authorized","purchase_authorized","payment_authorized","sale_authorized"):
            if result.get(key) is not False:
                raise ValueError(f"{key} must remain false")
        return attempt

    def get(self, attempt_key):
        if not isinstance(attempt_key,str) or not attempt_key.strip():
            raise ValueError("attempt_key must be a non-empty string")
        response=(self.client.table(self.table)
                  .select("attempt_key,intent_key,provider,requested_action,result,attempted_at")
                  .eq("attempt_key",attempt_key.strip()).limit(1).execute())
        rows=response.data or []
        return dict(rows[0]) if rows else None

    def append(self, attempt):
        attempt=self._validate(attempt)
        key=attempt["attempt_key"].strip()
        if self.get(key) is not None:
            raise ValueError("attempt_key already exists")
        payload={
            "attempt_key":key,
            "intent_key":attempt["intent_key"],
            "provider":attempt["provider"],
            "requested_action":attempt["requested_action"],
            "result":dict(attempt["result"]),
            "attempted_at":attempt["attempted_at"],
        }
        response=self.client.table(self.table).insert(payload).execute()
        rows=response.data or []
        if not rows:
            raise RuntimeError("sandbox attempt insert returned no row")
        return dict(rows[0])
