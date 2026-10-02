"""Supabase append-only repository for PG-016 human review decisions."""

TABLE_NAME = "warashibe_review_decisions"


class SupabaseReviewDecisionRepository:
    def __init__(self, client, table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client = client
        self.table = table

    @staticmethod
    def _validate(decision):
        if not isinstance(decision, dict):
            raise ValueError("decision must be a mapping")
        required = (
            "record_key",
            "identity_key",
            "decision",
            "reviewer_id",
            "reason",
            "reviewed_at",
        )
        missing = [key for key in required if key not in decision]
        if missing:
            raise ValueError("decision missing required keys: " + ",".join(missing))
        if decision.get("decision") not in {"approve", "reject"}:
            raise ValueError("invalid review decision")
        if decision.get("commerce_authorized") is not False:
            raise ValueError("commerce must remain blocked")
        return decision

    def get_by_record_key(self, record_key):
        if not isinstance(record_key, str) or not record_key.strip():
            raise ValueError("record_key must be a non-empty string")
        response = (
            self.client.table(self.table)
            .select("record_key,identity_key,decision,reviewer_id,reason,reviewed_at")
            .eq("record_key", record_key.strip())
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return dict(rows[0]) if rows else None

    def append(self, decision):
        decision = self._validate(decision)
        record_key = decision["record_key"].strip()
        if self.get_by_record_key(record_key) is not None:
            raise ValueError("record already reviewed")

        payload = {
            "record_key": record_key,
            "identity_key": decision["identity_key"],
            "decision": decision["decision"],
            "reviewer_id": decision["reviewer_id"],
            "reason": decision["reason"],
            "reviewed_at": decision["reviewed_at"],
        }
        response = self.client.table(self.table).insert(payload).execute()
        rows = response.data or []
        if not rows:
            raise RuntimeError("review decision insert returned no row")
        return dict(rows[0])
