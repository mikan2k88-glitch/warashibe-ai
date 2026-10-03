"""Supabase append-only repository for PG-030 receive inspections."""

TABLE_NAME="warashibe_receive_inspections"

class SupabaseReceiveInspectionRepository:
    def __init__(self,client,table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client=client
        self.table=table

    @staticmethod
    def _validate(inspection):
        if not isinstance(inspection,dict):
            raise ValueError("inspection must be a mapping")
        if inspection.get("status")!="inspection_complete":
            raise ValueError("inspection_complete required")
        if inspection.get("quantity")!=1 or inspection.get("quantity_received")!=1:
            raise ValueError("inspection must represent exactly one received item")
        if inspection.get("disposition") not in {"sale_ready","return_required","inspection_hold"}:
            raise ValueError("invalid disposition")
        if inspection.get("capital_basis_jpy") is None:
            raise ValueError("capital_basis_jpy required")
        return inspection

    def get(self,inspection_key):
        response=(self.client.table(self.table)
                  .select("inspection_key,receipt_key,provider,item_key,disposition,inspection,inspected_at")
                  .eq("inspection_key",inspection_key).limit(1).execute())
        rows=response.data or []
        return dict(rows[0]) if rows else None

    def append(self,inspection):
        inspection=self._validate(inspection)
        key=inspection["inspection_key"]
        if self.get(key) is not None:
            raise ValueError("inspection_key already exists")
        payload={
            "inspection_key":key,
            "receipt_key":inspection.get("receipt_key"),
            "provider":inspection.get("provider"),
            "item_key":inspection.get("item_key"),
            "disposition":inspection.get("disposition"),
            "inspection":dict(inspection),
            "inspected_at":inspection.get("inspected_at"),
        }
        response=self.client.table(self.table).insert(payload).execute()
        rows=response.data or []
        if not rows:
            raise RuntimeError("receive inspection insert returned no row")
        return dict(rows[0])
