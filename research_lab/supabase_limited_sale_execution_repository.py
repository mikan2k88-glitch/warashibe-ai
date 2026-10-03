"""Supabase append-only repository for PG-033 limited sale executions."""

TABLE_NAME="warashibe_limited_sale_executions"

class SupabaseLimitedSaleExecutionRepository:
    def __init__(self,client,table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client=client
        self.table=table

    def get_by_idempotency_key(self,key):
        response=(self.client.table(self.table)
                  .select("idempotency_key,decision_key,plan_key,item_key,marketplace,result,executed_at")
                  .eq("idempotency_key",key).limit(1).execute())
        rows=response.data or []
        return dict(rows[0]) if rows else None

    def append(self,row):
        if not isinstance(row,dict):
            raise ValueError("execution row must be a mapping")
        result=row.get("result")
        if not isinstance(result,dict) or result.get("status")!="limited_sale_listing_created":
            raise ValueError("limited_sale_listing_created result required")
        if result.get("execution_count")!=1:
            raise ValueError("execution_count must be one")
        if result.get("listing_created") is not True:
            raise ValueError("listing_created=True required")
        if result.get("sale_completed") is not False:
            raise ValueError("sale must remain incomplete at listing stage")
        key=row.get("idempotency_key")
        if self.get_by_idempotency_key(key) is not None:
            raise ValueError("idempotency key already exists")
        response=self.client.table(self.table).insert({
            "idempotency_key":key,
            "decision_key":row.get("decision_key"),
            "plan_key":row.get("plan_key"),
            "item_key":row.get("item_key"),
            "marketplace":row.get("marketplace"),
            "result":dict(result),
            "executed_at":row.get("executed_at"),
        }).execute()
        rows=response.data or []
        if not rows:
            raise RuntimeError("limited sale execution insert returned no row")
        return dict(rows[0])
