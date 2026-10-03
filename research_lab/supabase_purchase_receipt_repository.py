"""Supabase append-only repository for PG-029 purchase receipts."""

TABLE_NAME="warashibe_purchase_receipts"

class SupabasePurchaseReceiptRepository:
    def __init__(self,client,table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client=client
        self.table=table

    @staticmethod
    def _validate(receipt):
        if not isinstance(receipt,dict):
            raise ValueError("receipt must be a mapping")
        if receipt.get("status") not in {"purchase_receipt_reconciled","purchase_receipt_mismatch"}:
            raise ValueError("invalid receipt status")
        if receipt.get("quantity") != 1:
            raise ValueError("receipt must represent exactly one item")
        if receipt.get("capital_committed_jpy") != receipt.get("actual_total_charged_jpy"):
            raise ValueError("capital committed must equal actual total charged")
        return receipt

    def get(self,receipt_key):
        response=(self.client.table(self.table)
                  .select("receipt_key,idempotency_key,provider,item_key,provider_order_reference,receipt,reconciled_at")
                  .eq("receipt_key",receipt_key).limit(1).execute())
        rows=response.data or []
        return dict(rows[0]) if rows else None

    def append(self,receipt):
        receipt=self._validate(receipt)
        key=receipt["receipt_key"]
        if self.get(key) is not None:
            raise ValueError("receipt_key already exists")
        payload={
            "receipt_key":key,
            "idempotency_key":receipt.get("idempotency_key"),
            "provider":receipt.get("provider"),
            "item_key":receipt.get("item_key"),
            "provider_order_reference":receipt.get("provider_order_reference"),
            "receipt":dict(receipt),
            "reconciled_at":receipt.get("reconciled_at"),
        }
        response=self.client.table(self.table).insert(payload).execute()
        rows=response.data or []
        if not rows:
            raise RuntimeError("purchase receipt insert returned no row")
        return dict(rows[0])
