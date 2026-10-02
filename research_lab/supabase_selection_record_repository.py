"""Server-side Supabase repository for product selection records.

A trusted caller injects the Supabase client. This module never reads,
returns, or logs credentials.
"""

TABLE_NAME = "warashibe_selection_records"
REQUIRED_RECORD_KEYS = (
    "selected_candidate",
    "selection_reason",
    "candidate_result",
    "strategy_result",
    "simulation_result",
)


class SupabaseSelectionRecordRepository:
    def __init__(self, client, table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client = client
        self.table = table

    @staticmethod
    def _validate_key(record_key):
        if not isinstance(record_key, str) or not record_key.strip():
            raise ValueError("record_key must be a non-empty string")
        if len(record_key) > 200:
            raise ValueError("record_key is too long")
        return record_key.strip()

    @staticmethod
    def _validate_record(selection_record):
        if not isinstance(selection_record, dict):
            raise ValueError("selection_record must be a mapping")
        missing = [
            key for key in REQUIRED_RECORD_KEYS
            if key not in selection_record
        ]
        if missing:
            raise ValueError(
                "selection_record missing required keys: "
                + ",".join(missing)
            )
        if not isinstance(selection_record["selection_reason"], str):
            raise ValueError("selection_reason must be a string")
        return selection_record

    def get(self, record_key):
        key = self._validate_key(record_key)
        response = (
            self.client.table(self.table)
            .select("record_key,selection_record")
            .eq("record_key", key)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            return None
        row = rows[0]
        return {
            "record_key": str(row["record_key"]),
            "selection_record": row["selection_record"],
        }

    def append(self, record_key, selection_record):
        key = self._validate_key(record_key)
        record = self._validate_record(selection_record)

        if self.get(key) is not None:
            raise ValueError("record_key already exists")

        payload = {
            "record_key": key,
            "selection_record": record,
        }
        response = (
            self.client.table(self.table)
            .insert(payload)
            .execute()
        )
        rows = response.data or []
        if not rows:
            raise RuntimeError("selection record insert returned no row")

        row = rows[0]
        return {
            "record_key": str(row["record_key"]),
            "selection_record": row["selection_record"],
        }
