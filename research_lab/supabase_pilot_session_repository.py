"""Supabase append-only repository for PG-021 Human Pilot Sessions."""

TABLE_NAME = "warashibe_pilot_sessions"


class SupabasePilotSessionRepository:
    def __init__(self, client, table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client = client
        self.table = table

    @staticmethod
    def _validate(session):
        if not isinstance(session, dict):
            raise ValueError("session must be a mapping")
        required = (
            "session_key",
            "record_key",
            "plan_key",
            "identity_key",
            "session_state",
            "operator_id",
            "started_at",
        )
        missing = [key for key in required if key not in session]
        if missing:
            raise ValueError("session missing required keys: " + ",".join(missing))
        if session.get("status") != "pilot_session_ready":
            raise ValueError("pilot_session_ready required")
        if session.get("session_state") != "awaiting_human_final_confirmation":
            raise ValueError("invalid pilot session state")
        if session.get("quantity") != 1:
            raise ValueError("quantity must be one")
        if session.get("parallel_positions_allowed") is not False:
            raise ValueError("parallel positions must be disabled")
        for key in (
            "commerce_authorized",
            "external_action_authorized",
            "purchase_authorized",
            "payment_authorized",
            "sale_authorized",
        ):
            if session.get(key) is not False:
                raise ValueError(f"{key} must remain false")
        return session

    def get(self, session_key):
        if not isinstance(session_key, str) or not session_key.strip():
            raise ValueError("session_key must be a non-empty string")
        response = (
            self.client.table(self.table)
            .select("session_key,record_key,plan_key,identity_key,session_state,session,started_at")
            .eq("session_key", session_key.strip())
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return dict(rows[0]) if rows else None

    def append(self, session):
        session = self._validate(session)
        key = session["session_key"].strip()
        if self.get(key) is not None:
            raise ValueError("session_key already exists")
        payload = {
            "session_key": key,
            "record_key": session["record_key"],
            "plan_key": session["plan_key"],
            "identity_key": session["identity_key"],
            "session_state": session["session_state"],
            "session": dict(session),
            "started_at": session["started_at"],
        }
        response = self.client.table(self.table).insert(payload).execute()
        rows = response.data or []
        if not rows:
            raise RuntimeError("pilot session insert returned no row")
        return dict(rows[0])
