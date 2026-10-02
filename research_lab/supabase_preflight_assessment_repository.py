"""Supabase append-only repository for PG-020 pre-flight assessments."""

TABLE_NAME = "warashibe_preflight_assessments"


class SupabasePreflightAssessmentRepository:
    def __init__(self, client, table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client = client
        self.table = table

    @staticmethod
    def _validate(assessment):
        if not isinstance(assessment, dict):
            raise ValueError("assessment must be a mapping")
        required = (
            "preflight_key",
            "record_key",
            "plan_key",
            "identity_key",
            "preflight",
            "evaluated_at",
        )
        missing = [key for key in required if key not in assessment]
        if missing:
            raise ValueError("assessment missing required keys: " + ",".join(missing))
        preflight = assessment["preflight"]
        if not isinstance(preflight, dict):
            raise ValueError("preflight must be a mapping")
        if preflight.get("status") not in {"preflight_ready", "preflight_blocked"}:
            raise ValueError("invalid preflight status")
        if preflight.get("execution_mode") != "dry_run":
            raise ValueError("preflight must remain dry-run")
        for key in (
            "commerce_authorized",
            "external_action_authorized",
            "purchase_authorized",
            "payment_authorized",
            "sale_authorized",
        ):
            if preflight.get(key) is not False:
                raise ValueError(f"{key} must remain false")
        return assessment

    def get(self, preflight_key):
        if not isinstance(preflight_key, str) or not preflight_key.strip():
            raise ValueError("preflight_key must be a non-empty string")
        response = (
            self.client.table(self.table)
            .select("preflight_key,record_key,plan_key,identity_key,preflight,evaluated_at")
            .eq("preflight_key", preflight_key.strip())
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return dict(rows[0]) if rows else None

    def append(self, assessment):
        assessment = self._validate(assessment)
        key = str(assessment["preflight_key"]).strip()
        if self.get(key) is not None:
            raise ValueError("preflight_key already exists")
        payload = {
            "preflight_key": key,
            "record_key": assessment["record_key"],
            "plan_key": assessment["plan_key"],
            "identity_key": assessment["identity_key"],
            "preflight": dict(assessment["preflight"]),
            "evaluated_at": assessment["evaluated_at"],
        }
        response = self.client.table(self.table).insert(payload).execute()
        rows = response.data or []
        if not rows:
            raise RuntimeError("preflight assessment insert returned no row")
        return dict(rows[0])
