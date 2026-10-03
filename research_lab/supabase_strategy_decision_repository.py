"""Supabase append-only repository for Warashibe strategy decisions."""

TABLE_NAME = "warashibe_strategy_decisions"


class SupabaseStrategyDecisionRepository:
    def __init__(self, client, table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client = client
        self.table = table

    def latest(self, limit=20):
        if not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer")
        response = (
            self.client.table(self.table)
            .select(
                "decision_key,strategic_question,decision,rationale,evidence,"
                "expected_effect,invalidation_condition,result,status,decided_at"
            )
            .order("decided_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [dict(row) for row in (response.data or [])]

    def append(self, decision):
        if not isinstance(decision, dict):
            raise ValueError("decision must be a mapping")
        required = [
            "decision_key",
            "strategic_question",
            "decision",
            "rationale",
            "expected_effect",
            "invalidation_condition",
            "status",
            "decided_at",
        ]
        missing = [name for name in required if not decision.get(name)]
        if missing:
            raise ValueError(
                f"missing strategy decision fields: {', '.join(missing)}"
            )
        if decision["status"] not in {
            "active",
            "superseded",
            "invalidated",
            "completed",
        }:
            raise ValueError("invalid strategy decision status")

        row = {
            "decision_key": decision["decision_key"],
            "strategic_question": decision["strategic_question"],
            "decision": decision["decision"],
            "rationale": decision["rationale"],
            "evidence": dict(decision.get("evidence") or {}),
            "expected_effect": decision["expected_effect"],
            "invalidation_condition": decision["invalidation_condition"],
            "result": dict(decision.get("result") or {}),
            "status": decision["status"],
            "decided_at": decision["decided_at"],
        }
        response = self.client.table(self.table).insert(row).execute()
        rows = response.data or []
        if not rows:
            raise RuntimeError("strategy decision insert returned no row")
        return dict(rows[0])
