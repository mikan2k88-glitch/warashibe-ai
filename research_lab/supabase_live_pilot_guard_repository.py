"""Supabase append-only repository for PG-026 Live Pilot Guard results."""

TABLE_NAME="warashibe_live_pilot_guard_results"

class SupabaseLivePilotGuardRepository:
    def __init__(self,client,table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client=client
        self.table=table

    @staticmethod
    def _validate(record):
        if not isinstance(record,dict):
            raise ValueError("record must be a mapping")
        required=("guard_key","decision_key","intent_key","guard","evaluated_at")
        missing=[k for k in required if k not in record]
        if missing:
            raise ValueError("record missing required keys: "+",".join(missing))
        guard=record["guard"]
        if guard.get("status") not in {"live_pilot_guard_passed","live_pilot_guard_blocked"}:
            raise ValueError("invalid guard status")
        if guard.get("live_execution_authorized") is not False:
            raise ValueError("live execution must remain unauthorized")
        for key in ("commerce_authorized","external_action_authorized","purchase_authorized","payment_authorized","sale_authorized"):
            if guard.get(key) is not False:
                raise ValueError(f"{key} must remain false")
        return record

    def get(self,guard_key):
        response=(self.client.table(self.table)
                  .select("guard_key,decision_key,intent_key,guard,evaluated_at")
                  .eq("guard_key",guard_key).limit(1).execute())
        rows=response.data or []
        return dict(rows[0]) if rows else None

    def append(self,record):
        record=self._validate(record)
        if self.get(record["guard_key"]) is not None:
            raise ValueError("guard_key already exists")
        payload={
            "guard_key":record["guard_key"],
            "decision_key":record["decision_key"],
            "intent_key":record["intent_key"],
            "guard":dict(record["guard"]),
            "evaluated_at":record["evaluated_at"],
        }
        response=self.client.table(self.table).insert(payload).execute()
        rows=response.data or []
        if not rows:
            raise RuntimeError("guard insert returned no row")
        return dict(rows[0])
