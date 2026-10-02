"""Supabase append-only repository for PG-018 economic assessments."""

TABLE_NAME = "warashibe_economic_assessments"


class SupabaseEconomicAssessmentRepository:
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
            "assessment_key",
            "plan_key",
            "identity_key",
            "economics",
            "evaluated_at",
        )
        missing = [key for key in required if key not in assessment]
        if missing:
            raise ValueError("assessment missing required keys: " + ",".join(missing))
        economics = assessment["economics"]
        if not isinstance(economics, dict) or economics.get("status") != "economics_ready":
            raise ValueError("economics_ready payload required")
        if economics.get("execution_mode") != "dry_run":
            raise ValueError("dry-run economics required")
        for key in (
            "commerce_authorized",
            "external_action_authorized",
            "purchase_authorized",
            "payment_authorized",
            "sale_authorized",
        ):
            if economics.get(key) is not False:
                raise ValueError(f"{key} must remain false")
        return assessment

    def get(self, assessment_key):
        if not isinstance(assessment_key, str) or not assessment_key.strip():
            raise ValueError("assessment_key must be a non-empty string")
        response = (
            self.client.table(self.table)
            .select("assessment_key,plan_key,identity_key,economics,evaluated_at")
            .eq("assessment_key", assessment_key.strip())
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return dict(rows[0]) if rows else None

    def append(self, assessment):
        assessment = self._validate(assessment)
        key = str(assessment["assessment_key"]).strip()
        if self.get(key) is not None:
            raise ValueError("assessment_key already exists")

        payload = {
            "assessment_key": key,
            "plan_key": assessment["plan_key"],
            "identity_key": assessment["identity_key"],
            "economics": dict(assessment["economics"]),
            "evaluated_at": assessment["evaluated_at"],
        }
        response = self.client.table(self.table).insert(payload).execute()
        rows = response.data or []
        if not rows:
            raise RuntimeError("economic assessment insert returned no row")
        return dict(rows[0])
