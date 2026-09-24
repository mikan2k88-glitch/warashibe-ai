"""Offline checks for the secret-safe Supabase runtime smoke boundary."""

import os

from research_lab.supabase_runtime_smoke import runtime_readonly_smoke


class Response:
    data = []


class Query:
    def select(self, fields):
        assert fields == "id"
        return self

    def limit(self, value):
        assert value == 1
        return self

    def execute(self):
        return Response()


class Client:
    def table(self, name):
        assert name == "videos"
        return Query()


def main():
    old_url = os.environ.get("SUPABASE_URL")
    old_publishable = os.environ.get("SUPABASE_PUBLISHABLE_KEY")
    old_key = os.environ.get("SUPABASE_KEY")
    try:
        os.environ["SUPABASE_URL"] = "https://example.invalid"
        os.environ["SUPABASE_PUBLISHABLE_KEY"] = "test-only-key"
        os.environ.pop("SUPABASE_KEY", None)

        result = runtime_readonly_smoke(
            client_factory=lambda url, key: Client()
        )
        assert result == {
            "configured": True,
            "client_created": True,
            "read_ok": True,
            "reason": "ok",
            "row_count": 0,
        }
        assert "url" not in result and "key" not in result

        os.environ.pop("SUPABASE_URL", None)
        os.environ.pop("SUPABASE_PUBLISHABLE_KEY", None)
        result = runtime_readonly_smoke(client_factory=lambda url, key: Client())
        assert result["reason"] == "missing_environment"
        assert result["read_ok"] is False
    finally:
        if old_url is None:
            os.environ.pop("SUPABASE_URL", None)
        else:
            os.environ["SUPABASE_URL"] = old_url
        if old_publishable is None:
            os.environ.pop("SUPABASE_PUBLISHABLE_KEY", None)
        else:
            os.environ["SUPABASE_PUBLISHABLE_KEY"] = old_publishable
        if old_key is None:
            os.environ.pop("SUPABASE_KEY", None)
        else:
            os.environ["SUPABASE_KEY"] = old_key

    print("Supabase runtime smoke tests passed")


if __name__ == "__main__":
    main()
