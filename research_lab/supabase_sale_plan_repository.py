"""Supabase append-only repository for PG-031 sale plans."""

TABLE_NAME="warashibe_sale_plans"

class SupabaseSalePlanRepository:
    def __init__(self,client,table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client=client
        self.table=table

    @staticmethod
    def _validate(plan):
        if not isinstance(plan,dict):
            raise ValueError("plan must be a mapping")
        if plan.get("status")!="sale_plan_ready":
            raise ValueError("sale_plan_ready required")
        if plan.get("quantity")!=1:
            raise ValueError("sale plan must represent exactly one item")
        if plan.get("human_sale_decision_required") is not True:
            raise ValueError("human sale decision must be required")
        if plan.get("listing_authorized") is not False or plan.get("sale_authorized") is not False:
            raise ValueError("sale plan must not authorize listing or sale")
        return plan

    def get(self,plan_key):
        response=(self.client.table(self.table)
                  .select("plan_key,inspection_key,item_key,marketplace,plan,planned_at")
                  .eq("plan_key",plan_key).limit(1).execute())
        rows=response.data or []
        return dict(rows[0]) if rows else None

    def append(self,plan):
        plan=self._validate(plan)
        key=plan["plan_key"]
        if self.get(key) is not None:
            raise ValueError("plan_key already exists")
        payload={
            "plan_key":key,
            "inspection_key":plan.get("inspection_key"),
            "item_key":plan.get("item_key"),
            "marketplace":plan.get("marketplace"),
            "plan":dict(plan),
            "planned_at":plan.get("planned_at"),
        }
        response=self.client.table(self.table).insert(payload).execute()
        rows=response.data or []
        if not rows:
            raise RuntimeError("sale plan insert returned no row")
        return dict(rows[0])
