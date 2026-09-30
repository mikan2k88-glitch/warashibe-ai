"""Regression tests for repair history snapshots."""
import unittest

from research_lab.problem_repair_history_snapshot import build_repair_history_snapshot


class TestProblemRepairHistorySnapshot(unittest.TestCase):
    def ledger(self, *, cycle_id, repair_id, before_sha, after_sha, validation_status):
        return {
            "cycle_id": cycle_id,
            "repair_ids": (repair_id,),
            "head_before": before_sha,
            "head_after": after_sha,
            "scope": "research-lab",
            "single_repair_cycle": True,
            "repair_count": 1,
            "records": ({
                "repair_id": repair_id,
                "before_sha": before_sha,
                "after_sha": after_sha,
                "path": "research_lab/example.py",
                "expected_test": "python -m research_lab.test_example",
                "validation_status": validation_status,
                "repair_success": validation_status == "repair_validated_success",
                "rollback_candidate": validation_status == "repair_validated_failure",
                "scope": "research-lab",
                "single_file_only": True,
            },),
        }

    def assert_safe(self, result):
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)

    def test_snapshot_summarizes_contiguous_history(self):
        result = build_repair_history_snapshot([
            self.ledger(
                cycle_id="c1",
                repair_id="r1",
                before_sha="a",
                after_sha="b",
                validation_status="repair_validated_success",
            ),
            self.ledger(
                cycle_id="c2",
                repair_id="r2",
                before_sha="b",
                after_sha="c",
                validation_status="repair_validated_failure",
            ),
            self.ledger(
                cycle_id="c3",
                repair_id="r3",
                before_sha="c",
                after_sha="d",
                validation_status="repair_validated_success",
            ),
        ])
        self.assertEqual(result["status"], "repair_history_snapshot_ready")
        snapshot = result["snapshot"]
        self.assertEqual(snapshot["cycle_count"], 3)
        self.assertEqual(snapshot["repair_count"], 3)
        self.assertEqual(snapshot["success_count"], 2)
        self.assertEqual(snapshot["failure_count"], 1)
        self.assertEqual(snapshot["head_start"], "a")
        self.assertEqual(snapshot["head_end"], "d")
        self.assertIs(snapshot["continuous"], True)
        self.assertEqual(len(snapshot["cycles"]), 3)
        self.assert_safe(result)

    def test_broken_continuity_is_rejected(self):
        result = build_repair_history_snapshot([
            self.ledger(
                cycle_id="c1",
                repair_id="r1",
                before_sha="a",
                after_sha="b",
                validation_status="repair_validated_success",
            ),
            self.ledger(
                cycle_id="c2",
                repair_id="r2",
                before_sha="x",
                after_sha="y",
                validation_status="repair_validated_success",
            ),
        ])
        self.assertIn("continuity_not_validated", result["reasons"])
        self.assertIsNone(result["snapshot"])
        self.assert_safe(result)

    def test_nonterminal_validation_is_rejected(self):
        result = build_repair_history_snapshot([
            self.ledger(
                cycle_id="c1",
                repair_id="r1",
                before_sha="a",
                after_sha="b",
                validation_status="repair_validation_hold",
            ),
            self.ledger(
                cycle_id="c2",
                repair_id="r2",
                before_sha="b",
                after_sha="c",
                validation_status="repair_validated_success",
            ),
        ])
        self.assertIn("validation_not_terminal", result["reasons"])
        self.assert_safe(result)

    def test_missing_record_is_rejected(self):
        first = self.ledger(
            cycle_id="c1",
            repair_id="r1",
            before_sha="a",
            after_sha="b",
            validation_status="repair_validated_success",
        )
        first["records"] = ()
        result = build_repair_history_snapshot([
            first,
            self.ledger(
                cycle_id="c2",
                repair_id="r2",
                before_sha="b",
                after_sha="c",
                validation_status="repair_validated_success",
            ),
        ])
        self.assertIn("invalid_ledger_records", result["reasons"])
        self.assert_safe(result)

    def test_duplicate_cycle_or_repair_is_rejected_via_continuity_gate(self):
        result = build_repair_history_snapshot([
            self.ledger(
                cycle_id="same",
                repair_id="r1",
                before_sha="a",
                after_sha="b",
                validation_status="repair_validated_success",
            ),
            self.ledger(
                cycle_id="same",
                repair_id="r2",
                before_sha="b",
                after_sha="c",
                validation_status="repair_validated_success",
            ),
        ])
        self.assertIn("continuity_not_validated", result["reasons"])
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
