"""Supabase append-only repository for PG-027 live-adapter validation artifacts."""

TABLE_NAME="warashibe_live_adapter_validations"


class SupabaseLiveAdapterValidationRepository:
    def __init__(self,client,table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client=client
        self.table=table

    @staticmethod
    def _validate(record):
        if not isinstance(record,dict):
            raise ValueError("record must be a mapping")
        required=("validation_key","provider","item_key","validation","validated_at")
        missing=[k for k in required if k not in record]
        if missing:
            raise ValueError("record missing required keys: "+",".join(missing))
        validation=record["validation"]
        if not isinstance(validation,dict):
            raise ValueError("validation must be a mapping")
        if validation.get("status")!="live_adapter_validation_ready":
            raise ValueError("live_adapter_validation_ready required")
        if validation.get("validation_passed") is not True:
            raise ValueError("validation_passed=True required")
        if validation.get("eligible_for_human_final_buy") is not True:
            raise ValueError("human final buy eligibility required")
        if validation.get("order_submission_authorized") is not False:
            raise ValueError("order submission must remain unauthorized")
        if validation.get("network_call_attempted") is not False:
            raise ValueError("network calls must remain unattempted")
        if validation.get("external_write_attempted") is not False:
            raise ValueError("external writes must remain unattempted")
        if validation.get("live_execution_authorized") is not False:
            raise ValueError("live execution must remain unauthorized")
        if validation.get("commerce_authorized") is not False:
            raise ValueError("commerce must remain unauthorized")
        return record

    def get(self,validation_key):
        if not isinstance(validation_key,str) or not validation_key.strip():
            raise ValueError("validation_key must be a non-empty string")
        response=(self.client.table(self.table)
                  .select("validation_key,provider,item_key,validation,validated_at")
                  .eq("validation_key",validation_key.strip()).limit(1).execute())
        rows=response.data or []
        return dict(rows[0]) if rows else None

    def append(self,record):
        record=self._validate(record)
        key=record["validation_key"].strip()
        if self.get(key) is not None:
            raise ValueError("validation_key already exists")
        payload={
            "validation_key":key,
            "provider":record["provider"],
            "item_key":record["item_key"],
            "validation":dict(record["validation"]),
            "validated_at":record["validated_at"],
        }
        response=self.client.table(self.table).insert(payload).execute()
        rows=response.data or []
        if not rows:
            raise RuntimeError("live-adapter validation insert returned no row")
        return dict(rows[0])
