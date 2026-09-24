"""Offline contract test for SupabaseOutcomeRepository."""

from types import SimpleNamespace

from research_lab.outcome_repository import validate_repository
from research_lab.raw_outcome_calibration import SaleOutcome
from research_lab.supabase_outcome_repository import SupabaseOutcomeRepository


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows
        self.filtered = rows

    def select(self, _columns):
        self.filtered = self.rows
        return self

    def eq(self, column, value):
        self.filtered = [row for row in self.rows if row.get(column) == value]
        return self

    def insert(self, payload):
        self.rows.append(dict(payload))
        self.filtered = self.rows
        return self

    def execute(self):
        return SimpleNamespace(data=list(self.filtered))


class FakeClient:
    def __init__(self):
        self.rows = []

    def table(self, _name):
        return FakeQuery(self.rows)


def main():
    repo = validate_repository(SupabaseOutcomeRepository(FakeClient()))
    assert repo.stats()["mode"] == "waiting"
    assert repo.append(SaleOutcome("camera-a", True, 2.0)) == 1
    assert repo.append(SaleOutcome("camera-a", False, 5.0)) == 2
    assert repo.append(SaleOutcome("book-b", True, 1.0)) == 3
    camera = repo.for_opportunity("camera-a")
    assert len(camera) == 2 and camera[0].sold and not camera[1].sold
    assert repo.stats() == {
        "mode": "persisted_supabase",
        "total": 3,
        "sold": 2,
        "failed": 1,
        "opportunities": 2,
    }
    print("Supabase outcome repository contract: PASS")


if __name__ == "__main__":
    main()
