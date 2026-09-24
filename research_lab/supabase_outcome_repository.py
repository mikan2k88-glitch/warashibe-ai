"""Supabase-compatible outcome repository without credentials or network setup.

The adapter targets the small OutcomeRepository contract.  A Supabase/PostgREST
client is injected by the caller, so research tests need no secrets and make no
external writes.
"""

from research_lab.raw_outcome_calibration import SaleOutcome


class SupabaseOutcomeRepository:
    def __init__(self, client, table="warashibe_sale_outcomes"):
        self.client = client
        self.table = table

    @staticmethod
    def _decode(row):
        return SaleOutcome(
            opportunity_key=str(row["opportunity_key"]),
            sold=bool(row["sold"]),
            days_to_outcome=row.get("days_to_outcome"),
        )

    def load(self):
        response = self.client.table(self.table).select(
            "opportunity_key,sold,days_to_outcome"
        ).execute()
        return [self._decode(row) for row in (response.data or [])]

    def append(self, outcome):
        payload = {
            "opportunity_key": outcome.opportunity_key,
            "sold": outcome.sold,
            "days_to_outcome": outcome.days_to_outcome,
        }
        self.client.table(self.table).insert(payload).execute()
        return len(self.load())

    def for_opportunity(self, opportunity_key):
        response = (
            self.client.table(self.table)
            .select("opportunity_key,sold,days_to_outcome")
            .eq("opportunity_key", opportunity_key)
            .execute()
        )
        return [self._decode(row) for row in (response.data or [])]

    def stats(self):
        rows = self.load()
        sold = sum(1 for row in rows if row.sold)
        return {
            "mode": "persisted_supabase" if rows else "waiting",
            "total": len(rows),
            "sold": sold,
            "failed": len(rows) - sold,
            "opportunities": len({row.opportunity_key for row in rows}),
        }
