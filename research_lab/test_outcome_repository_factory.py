"""Offline checks for safe repository backend selection."""

from tempfile import TemporaryDirectory
from pathlib import Path

from research_lab.live_outcome_store import OutcomeStore
from research_lab.outcome_repository_factory import build_outcome_repository
from research_lab.supabase_outcome_repository import SupabaseOutcomeRepository


def main():
    with TemporaryDirectory() as tmp:
        repo = build_outcome_repository("json", path=Path(tmp) / "outcomes.json")
        assert isinstance(repo, OutcomeStore)
        assert repo.stats()["mode"] == "waiting"

    marker = object()
    remote = build_outcome_repository("supabase", supabase_client=marker, table="research_outcomes")
    assert isinstance(remote, SupabaseOutcomeRepository)
    assert remote.client is marker
    assert remote.table == "research_outcomes"

    try:
        build_outcome_repository("supabase")
    except ValueError as exc:
        assert "injected client" in str(exc)
    else:
        raise AssertionError("Supabase backend must fail closed without a client")

    try:
        build_outcome_repository("unknown")
    except ValueError as exc:
        assert "unsupported" in str(exc)
    else:
        raise AssertionError("Unknown backend must fail closed")

    print("outcome_repository_factory: ok")


if __name__ == "__main__":
    main()
