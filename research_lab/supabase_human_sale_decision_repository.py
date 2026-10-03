"""Supabase append-only repository for PG-032 human sale decisions."""

TABLE_NAME="warashibe_human_sale_decisions"

class SupabaseHumanSaleDecisionRepository:
    def __init__(self,client,table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client=client
        self.table=table

    @staticmethod
    def _validate(decision):
        if not isinstance(decision,dict):
            raise ValueError("decision must be a mapping")
        if decision.get("status")!="human_sale_decision_recorded":
            raise ValueError("human_sale_decision_recorded required")
        if decision.get("decision") not in {"sell","do_not_sell"}:
            raise ValueError("invalid decision")
        if decision.get("quantity")!=1:
            raise ValueError("decision must represent exactly one item")
        if decision.get("listing_created") is not False or decision.get("sale_completed") is not False:
            raise ValueError("decision artifact must not create or complete a sale")
        return decision

    def get(self,decision_key):
        response=(self.client.table(self.table)
                  .select("decision_key,plan_key,item_key,marketplace,decision,decision_payload,decided_at,valid_until")
                  .eq("decision_key",decision_key).limit(1).execute())
        rows=response.data or []
        return dict(rows[0]) if rows else None

    def append(self,decision):
        decision=self._validate(decision)
        key=decision["decision_key"]
        if self.get(key) is not None:
            raise ValueError("decision_key already exists")
        payload={
            "decision_key":key,
            "plan_key":decision.get("plan_key"),
            "item_key":decision.get("item_key"),
            "marketplace":decision.get("marketplace"),
            "decision":decision.get("decision"),
            "decision_payload":dict(decision),
            "decided_at":decision.get("decided_at"),
            "valid_until":decision.get("valid_until"),
        }
        response=self.client.table(self.table).insert(payload).execute()
        rows=response.data or []
        if not rows:
            raise RuntimeError("human sale decision insert returned no row")
        return dict(rows[0])
