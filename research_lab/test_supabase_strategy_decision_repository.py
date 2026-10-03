"""Append-only Supabase strategy decision repository contract tests."""

from research_lab.supabase_strategy_decision_repository import (
    SupabaseStrategyDecisionRepository,
)


class Response:
    def __init__(self, data):
        self.data = data


class Query:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.inserted = None
        self.limit_value = None

    def select(self, *_args):
        return self

    def order(self, *_args, **_kwargs):
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def insert(self, row):
        self.inserted = dict(row)
        return self

    def execute(self):
        if self.inserted is not None:
            return Response([dict(self.inserted)])
        return Response(self.rows[: self.limit_value or len(self.rows)])


class Client:
    def __init__(self):
        self.query = Query([
            {
                "decision_key": "hq-v1-initial",
                "strategic_question": "What is the current bottleneck?",
                "decision": "real_pilot_readiness",
                "status": "active",
                "decided_at": "2026-10-03T09:10:00+00:00",
            }
        ])
        self.table_name = None

    def table(self, name):
        self.table_name = name
        return self.query


def main():
    client = Client()
    repo = SupabaseStrategyDecisionRepository(client)

    latest = repo.latest(limit=1)
    assert client.table_name == "warashibe_strategy_decisions"
    assert latest[0]["decision_key"] == "hq-v1-initial"

    row = repo.append({
        "decision_key": "hq-v1-initial",
        "strategic_question": "What is the current bottleneck?",
        "decision": "real_pilot_readiness",
        "rationale": "Synthetic loop is complete but live proof is not.",
        "evidence": {"synthetic_loop_complete": True},
        "expected_effect": "Prepare one controlled live proof.",
        "invalidation_condition": "Live proof shows a different bottleneck.",
        "result": {},
        "status": "active",
        "decided_at": "2026-10-03T09:10:00+00:00",
    })
    assert row["decision_key"] == "hq-v1-initial"
    assert row["status"] == "active"

    assert not hasattr(repo, "update")
    assert not hasattr(repo, "delete")

    print("Supabase strategy decision repository contract tests passed")


if __name__ == "__main__":
    main()
