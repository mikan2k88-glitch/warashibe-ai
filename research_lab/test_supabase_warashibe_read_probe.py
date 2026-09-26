from research_lab.supabase_warashibe_read_probe import TABLES, probe


class Query:
    def select(self, columns):
        assert columns == "id"
        return self

    def limit(self, count):
        assert count == 1
        return self

    def execute(self):
        return object()


class Client:
    def __init__(self):
        self.visited = []

    def table(self, name):
        self.visited.append(name)
        return Query()


def main():
    result = probe(environ={})
    assert result["status"] == "not_configured"
    assert result["read_ok"] is False
    client = Client()
    result = probe(
        environ={"SUPABASE_URL": "https://example.invalid",
                 "SUPABASE_KEY": "offline-only-fixture"},
        client_factory=lambda url, key: client,
    )
    assert result["read_ok"] is True
    assert client.visited == list(TABLES)
    assert "offline-only-fixture" not in str(result)
    print("Offline read probe tests passed")


if __name__ == "__main__":
    main()
