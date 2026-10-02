"""Server-side Supabase repository for PG-015 cross-market records."""

TABLE_NAME = "warashibe_cross_market_records"


class SupabaseCrossMarketRecordRepository:
    def __init__(self, client, table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client = client
        self.table = table

    @staticmethod
    def _validate_record(record):
        if not isinstance(record, dict):
            raise ValueError("record must be a mapping")
        required = (
            "record_key",
            "identity_key",
            "comparison",
            "proposal",
            "observed_at",
            "captured_at",
        )
        missing = [key for key in required if key not in record]
        if missing:
            raise ValueError("record missing required keys: " + ",".join(missing))
        if not isinstance(record["record_key"], str) or not record["record_key"].strip():
            raise ValueError("record_key must be a non-empty string")
        if len(record["record_key"].strip()) > 200:
            raise ValueError("record_key is too long")
        if not isinstance(record["identity_key"], str) or not record["identity_key"].strip():
            raise ValueError("identity_key must be a non-empty string")
        if not isinstance(record["comparison"], dict):
            raise ValueError("comparison must be a mapping")
        if not isinstance(record["proposal"], dict):
            raise ValueError("proposal must be a mapping")
        if record["proposal"].get("commerce_authorized") is not False:
            raise ValueError("commerce must remain blocked")
        return record

    def get(self, record_key):
        if not isinstance(record_key, str) or not record_key.strip():
            raise ValueError("record_key must be a non-empty string")
        response = (
            self.client.table(self.table)
            .select("record_key,identity_key,comparison,proposal,observed_at,captured_at")
            .eq("record_key", record_key.strip())
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            return None
        return dict(rows[0])

    def append(self, record):
        record = self._validate_record(record)
        key = record["record_key"].strip()
        if self.get(key) is not None:
            raise ValueError("record_key already exists")

        payload = {
            "record_key": key,
            "identity_key": record["identity_key"],
            "comparison": record["comparison"],
            "proposal": record["proposal"],
            "observed_at": record["observed_at"],
            "captured_at": record["captured_at"],
        }
        response = self.client.table(self.table).insert(payload).execute()
        rows = response.data or []
        if not rows:
            raise RuntimeError("cross-market record insert returned no row")
        return dict(rows[0])

    def latest_for_identity(self, identity_key):
        if not isinstance(identity_key, str) or not identity_key.strip():
            raise ValueError("identity_key must be a non-empty string")
        response = (
            self.client.table(self.table)
            .select("record_key,identity_key,comparison,proposal,observed_at,captured_at")
            .eq("identity_key", identity_key.strip())
            .order("captured_at", desc=True)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return dict(rows[0]) if rows else None
