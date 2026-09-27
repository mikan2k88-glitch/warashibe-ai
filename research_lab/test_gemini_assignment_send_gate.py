"""Offline tests of persistent Gemini assignment send gate; no API calls."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

from research_lab.gemini_assignment_send_gate import (
    consume_assignment_gate, initialize_assignment_gate, make_assignment_gate,
)


def run_tests():
    with TemporaryDirectory() as directory:
        path = Path(directory) / "send-ledger.sqlite3"
        assert consume_assignment_gate(path, "assignment-1", "run-1") is False
        initialize_assignment_gate(path)
        gate = make_assignment_gate(path, "assignment-1", "run-1")
        assert gate() is True
        assert gate() is False
        assert consume_assignment_gate(path, "assignment-1", "other-run") is False

        # New consumer simulates a new process opening the existing ledger.
        assert make_assignment_gate(path, "assignment-1", "run-1")() is False
        assert consume_assignment_gate(path, "", "run-2") is False
        assert consume_assignment_gate(path, "assignment-2", "") is False

        with ThreadPoolExecutor(max_workers=8) as executor:
            outcomes = list(executor.map(
                lambda _: consume_assignment_gate(path, "concurrent", "run-3"),
                range(16),
            ))
        assert outcomes.count(True) == 1
        assert outcomes.count(False) == 15

        # Reinitialization preserves reservations rather than resetting them.
        initialize_assignment_gate(path)
        assert consume_assignment_gate(path, "concurrent", "run-3") is False
        assert consume_assignment_gate(path, "assignment-2", "run-2") is True
        assert consume_assignment_gate(path.parent / "missing.sqlite3", "new", "run") is False

        # A damaged or replaced ledger must stop sends rather than be recreated.
        damaged = path.parent / "damaged.sqlite3"
        damaged.write_bytes(b"not a sqlite database")
        assert consume_assignment_gate(damaged, "new", "run") is False
        assert damaged.read_bytes() == b"not a sqlite database"
        empty_schema = path.parent / "empty-schema.sqlite3"
        empty_schema.touch()
        assert consume_assignment_gate(empty_schema, "new", "run") is False
        assert empty_schema.is_file()


if __name__ == "__main__":
    run_tests()
    print("Persistent Gemini assignment gate offline tests passed")
