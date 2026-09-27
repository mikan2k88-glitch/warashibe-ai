"""Offline end-to-end rehearsal: durable reservation -> mocked Gemini receipt.

No real network, key, scheduled send, or downstream execution is authorized.
"""
from pathlib import Path
from tempfile import TemporaryDirectory

from research_lab.gemini_assignment_send_gate import initialize_assignment_gate, make_assignment_gate
from research_lab.gemini_live_probe import send_assignment_once
from research_lab.test_gemini_assignment_offline import assignment, response_for, FakeResponse


def run_tests():
    item = assignment()
    with TemporaryDirectory() as directory:
        ledger = Path(directory) / "assignment.sqlite3"
        initialize_assignment_gate(ledger)
        calls = []

        def transport(req, timeout):
            calls.append(item["assignment_id"])
            assert timeout == 20
            return FakeResponse(response_for(item))

        def send(run="offline-source"):
            return send_assignment_once(
                item, run, "offline-placeholder",
                make_assignment_gate(ledger, item["assignment_id"], run), transport,
            )

        first = send()
        assert first["status"] == "received", first
        assert first["execution_authorized"] is False
        assert first["codex_execution_authorized"] is False
        assert first["usage"]["total_tokens"] == 32
        assert send()["status"] == "blocked"
        assert send("different-run")["status"] == "blocked"
        assert len(calls) == 1

        # An uncertain delivery consumes the durable gate: no automatic retry.
        failed_item = dict(item, assignment_id=item["assignment_id"] + "-uncertain")
        def uncertain(req, timeout):
            calls.append("uncertain")
            raise TimeoutError("simulated timeout")
        gate = make_assignment_gate(ledger, failed_item["assignment_id"], "offline-source")
        failed = send_assignment_once(failed_item, "offline-source", "offline-placeholder", gate, uncertain)
        assert failed["status"] == "failed" and failed["reason"] == "network_error"
        blocked = send_assignment_once(failed_item, "offline-source", "offline-placeholder",
            make_assignment_gate(ledger, failed_item["assignment_id"], "offline-source"), uncertain)
        assert blocked["status"] == "blocked"
        assert calls.count("uncertain") == 1

        # Missing durable ledger must fail closed without a transport call.
        ledger.unlink()
        assert send()["status"] == "blocked"
        assert len(calls) == 2


if __name__ == "__main__":
    run_tests()
    print("Durable Gemini assignment integration rehearsal passed (offline only)")
