"""Offline checks for backend-neutral repository observability."""

from research_lab.outcome_learning_loop import repository_observability


class FakeRepository:
    def stats(self):
        return {
            "mode": "fake",
            "total": 5,
            "sold": 3,
            "failed": 2,
            "opportunities": 4,
            "secret": "must-not-leak",
        }


def main():
    snapshot = repository_observability(store=FakeRepository())
    assert snapshot == {
        "backend": "injected",
        "mode": "fake",
        "total": 5,
        "sold": 3,
        "failed": 2,
        "opportunities": 4,
    }
    assert "secret" not in snapshot
    print("repository observability tests passed")


if __name__ == "__main__":
    main()
