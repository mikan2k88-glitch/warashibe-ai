"""Offline fake-client test. Never connects to Supabase."""
from types import SimpleNamespace
from research_lab.supabase_outcome_write_probe import probe


class Query:
    def __init__(self, rows):
        self.rows = rows
        self.filters = {}
        self.operation = "select"
        self.payload = None

    def insert(self, payload):
        self.operation, self.payload = "insert", payload
        return self

    def select(self, columns):
        self.operation = "select"
        return self

    def delete(self):
        self.operation = "delete"
        return self

    def eq(self, key, value):
        self.filters[key] = value
        return self

    def execute(self):
        if self.operation == "insert":
            row = dict(self.payload, id=len(self.rows) + 1)
            self.rows.append(row)
            return SimpleNamespace(data=[row])
        matching = [r for r in self.rows if all(r.get(k) == v for k, v in self.filters.items())]
        if self.operation == "delete":
            for row in matching:
                self.rows.remove(row)
        return SimpleNamespace(data=matching)


class Client:
    def __init__(self):
        self.rows = [{"id": 1, "opportunity_key": "existing", "sold": True}]

    def table(self, name):
        assert name == "warashibe_sale_outcomes"
        return Query(self.rows)


def main():
    client = Client()
    result = probe(client, token="offline-test")
    assert result == {"status": "ok", "write_read_ok": True,
                      "cleanup_ok": True, "manual_review_required": False}
    assert len(client.rows) == 1
    assert client.rows[0]["opportunity_key"] == "existing"
    print("Supabase outcome write probe offline: PASS")


if __name__ == "__main__":
    main()
