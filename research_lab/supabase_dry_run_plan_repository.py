"""Supabase append-only repository for PG-017 dry-run commerce plans."""

TABLE_NAME = "warashibe_dry_run_plans"


class SupabaseDryRunPlanRepository:
    def __init__(self, client, table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client = client
        self.table = table

    @staticmethod
    def _validate(plan):
        if not isinstance(plan, dict):
            raise ValueError("plan must be a mapping")
        required = (
            "plan_key",
            "source_record_key",
            "identity_key",
            "review_decision",
            "candidate_name",
            "candidate_source",
            "purchase_price_jpy",
            "generated_at",
            "execution_mode",
        )
        missing = [key for key in required if key not in plan]
        if missing:
            raise ValueError("plan missing required keys: " + ",".join(missing))
        if plan.get("review_decision") != "approve":
            raise ValueError("approved review required")
        if plan.get("execution_mode") != "dry_run":
            raise ValueError("dry-run execution mode required")
        for key in (
            "commerce_authorized",
            "external_action_authorized",
            "purchase_authorized",
            "payment_authorized",
            "sale_authorized",
        ):
            if plan.get(key) is not False:
                raise ValueError(f"{key} must remain false")
        return plan

    def get(self, plan_key):
        if not isinstance(plan_key, str) or not plan_key.strip():
            raise ValueError("plan_key must be a non-empty string")
        response = (
            self.client.table(self.table)
            .select("plan_key,source_record_key,identity_key,review_decision,plan,generated_at")
            .eq("plan_key", plan_key.strip())
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return dict(rows[0]) if rows else None

    def append(self, plan):
        plan = self._validate(plan)
        key = plan["plan_key"].strip()
        if self.get(key) is not None:
            raise ValueError("plan_key already exists")

        payload = {
            "plan_key": key,
            "source_record_key": plan["source_record_key"],
            "identity_key": plan["identity_key"],
            "review_decision": plan["review_decision"],
            "plan": dict(plan),
            "generated_at": plan["generated_at"],
        }
        response = self.client.table(self.table).insert(payload).execute()
        rows = response.data or []
        if not rows:
            raise RuntimeError("dry-run plan insert returned no row")
        return dict(rows[0])
