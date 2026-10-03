"""Supabase append-only repository for PG-034 trade settlements."""

TABLE_NAME="warashibe_trade_settlements"

class SupabaseTradeSettlementRepository:
    def __init__(self,client,table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client=client
        self.table=table

    def get(self,settlement_key):
        response=(self.client.table(self.table)
                  .select("settlement_key,listing_idempotency_key,item_key,marketplace,settlement,settled_at")
                  .eq("settlement_key",settlement_key).limit(1).execute())
        rows=response.data or []
        return dict(rows[0]) if rows else None

    def append(self,settlement):
        if not isinstance(settlement,dict):
            raise ValueError("settlement must be a mapping")
        if settlement.get("status")!="trade_settled":
            raise ValueError("trade_settled required")
        if settlement.get("quantity")!=1:
            raise ValueError("settlement must represent exactly one item")
        if settlement.get("sale_completed") is not True or settlement.get("settlement_recorded") is not True:
            raise ValueError("completed sale and settlement required")
        if settlement.get("capital_state")!="ready_for_next_candidate":
            raise ValueError("next-capital state required")
        key=settlement.get("settlement_key")
        if self.get(key) is not None:
            raise ValueError("settlement_key already exists")
        response=self.client.table(self.table).insert({
            "settlement_key":key,
            "listing_idempotency_key":settlement.get("listing_idempotency_key"),
            "item_key":settlement.get("item_key"),
            "marketplace":settlement.get("marketplace"),
            "settlement":dict(settlement),
            "settled_at":settlement.get("settled_at"),
        }).execute()
        rows=response.data or []
        if not rows:
            raise RuntimeError("trade settlement insert returned no row")
        return dict(rows[0])
