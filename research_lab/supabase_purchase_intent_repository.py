"""Supabase append-only repository for PG-022 Purchase Intent Records."""

TABLE_NAME = "warashibe_purchase_intents"


class SupabasePurchaseIntentRepository:
    def __init__(self, client, table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client = client
        self.table = table

    @staticmethod
    def _validate(intent):
        if not isinstance(intent, dict):
            raise ValueError("intent must be a mapping")
        required = (
            "intent_key",
            "session_key",
            "record_key",
            "plan_key",
            "identity_key",
            "reviewer_id",
            "confirmed_at",
            "expires_at",
            "max_purchase_price_jpy",
            "max_total_cost_jpy",
        )
        missing = [key for key in required if key not in intent]
        if missing:
            raise ValueError("intent missing required keys: " + ",".join(missing))
        if intent.get("status") != "purchase_intent_recorded":
            raise ValueError("purchase_intent_recorded required")
        if intent.get("intent_type") != "human_purchase_intent":
            raise ValueError("human purchase intent required")
        if intent.get("quantity") != 1:
            raise ValueError("quantity must be one")
        if intent.get("parallel_positions_allowed") is not False:
            raise ValueError("parallel positions must remain disabled")
        if intent.get("order_submission_authorized") is not False:
            raise ValueError("order submission must remain blocked")
        for key in (
            "commerce_authorized",
            "external_action_authorized",
            "purchase_authorized",
            "payment_authorized",
            "sale_authorized",
        ):
            if intent.get(key) is not False:
                raise ValueError(f"{key} must remain false")
        return intent

    def get(self, intent_key):
        if not isinstance(intent_key, str) or not intent_key.strip():
            raise ValueError("intent_key must be a non-empty string")
        response = (
            self.client.table(self.table)
            .select("intent_key,session_key,record_key,plan_key,identity_key,intent,confirmed_at,expires_at")
            .eq("intent_key", intent_key.strip())
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return dict(rows[0]) if rows else None

    def get_by_session_key(self, session_key):
        if not isinstance(session_key, str) or not session_key.strip():
            raise ValueError("session_key must be a non-empty string")
        response = (
            self.client.table(self.table)
            .select("intent_key,session_key,record_key,plan_key,identity_key,intent,confirmed_at,expires_at")
            .eq("session_key", session_key.strip())
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return dict(rows[0]) if rows else None

    def append(self, intent):
        intent = self._validate(intent)
        key = intent["intent_key"].strip()
        if self.get(key) is not None:
            raise ValueError("intent_key already exists")
        if self.get_by_session_key(intent["session_key"]) is not None:
            raise ValueError("session already has a purchase intent")

        payload = {
            "intent_key": key,
            "session_key": intent["session_key"],
            "record_key": intent["record_key"],
            "plan_key": intent["plan_key"],
            "identity_key": intent["identity_key"],
            "intent": dict(intent),
            "confirmed_at": intent["confirmed_at"],
            "expires_at": intent["expires_at"],
        }
        response = self.client.table(self.table).insert(payload).execute()
        rows = response.data or []
        if not rows:
            raise RuntimeError("purchase intent insert returned no row")
        return dict(rows[0])
