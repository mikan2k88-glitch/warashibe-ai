"""Supabase append-only repository for PG-025 Human Go/No-Go decisions."""

TABLE_NAME="warashibe_live_pilot_decisions"

class SupabaseLivePilotDecisionRepository:
    def __init__(self,client,table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client=client
        self.table=table

    @staticmethod
    def _validate(decision):
        if not isinstance(decision,dict):
            raise ValueError("decision must be a mapping")
        required=("decision_key","decision","source_audit_key","decided_at","valid_until","reviewer_id","pilot_scope")
        missing=[k for k in required if k not in decision]
        if missing:
            raise ValueError("decision missing required keys: "+",".join(missing))
        if decision.get("status")!="human_go_no_go_recorded":
            raise ValueError("human_go_no_go_recorded required")
        if decision.get("decision") not in {"go","no_go"}:
            raise ValueError("invalid decision")
        if decision.get("live_execution_authorized") is not False:
            raise ValueError("live execution must remain unauthorized")
        for key in ("commerce_authorized","external_action_authorized","purchase_authorized","payment_authorized","sale_authorized"):
            if decision.get(key) is not False:
                raise ValueError(f"{key} must remain false")
        return decision

    def get(self,decision_key):
        response=(self.client.table(self.table)
                  .select("decision_key,source_audit_key,decision,reviewer_id,pilot_scope,decided_at,valid_until,decision_payload")
                  .eq("decision_key",decision_key).limit(1).execute())
        rows=response.data or []
        return dict(rows[0]) if rows else None

    def append(self,decision):
        decision=self._validate(decision)
        if self.get(decision["decision_key"]) is not None:
            raise ValueError("decision_key already exists")
        payload={
            "decision_key":decision["decision_key"],
            "source_audit_key":decision["source_audit_key"],
            "decision":decision["decision"],
            "reviewer_id":decision["reviewer_id"],
            "pilot_scope":decision["pilot_scope"],
            "decided_at":decision["decided_at"],
            "valid_until":decision["valid_until"],
            "decision_payload":dict(decision),
        }
        response=self.client.table(self.table).insert(payload).execute()
        rows=response.data or []
        if not rows:
            raise RuntimeError("decision insert returned no row")
        return dict(rows[0])
