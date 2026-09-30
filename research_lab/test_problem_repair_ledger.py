"""Regression tests for the single-repair cycle ledger gate."""
import unittest

from research_lab.problem_repair_ledger import (
    append_repair_to_ledger,
    build_repair_ledger,
)


class TestProblemRepairLedger(unittest.TestCase):
    def setUp(self):
        self.record = {
            "repair_id": "repair-001",
            "before_sha": "before123",
            "after_sha": "after456",
            "path": "research_lab/example.py",
            "expected_test": "python -m research_lab.test_example",
            "validation_status": "repair_validated_success",
            "repair_success": True,
            "rollback_candidate": False,
            "scope": "research-lab",
            "single_file_only": True,
        }

    def assert_safe(self, result):
        self.assertIs(result["cycle_closed"], True)
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)

    def test_one_repair_cycle_builds_ledger(self):
        result = build_repair_ledger(
            cycle_id="cycle-001",
            records=[self.record],
        )
        self.assertEqual(result["status"], "repair_ledger_ready")
        self.assertEqual(result["ledger"]["repair_count"], 1)
        self.assertEqual(result["ledger"]["repair_ids"], ("repair-001",))
        self.assertEqual(result["ledger"]["head_before"], "before123")
        self.assertEqual(result["ledger"]["head_after"], "after456")
        self.assertIs(result["ledger"]["single_repair_cycle"], True)
        self.assert_safe(result)

    def test_multiple_repairs_in_one_cycle_are_rejected(self):
        second = dict(
            self.record,
            repair_id="repair-002",
            before_sha="after456",
            after_sha="after789",
        )
        result = build_repair_ledger(
            cycle_id="cycle-001",
            records=[self.record, second],
        )
        self.assertIn("multiple_repairs_in_cycle", result["reasons"])
        self.assertIsNone(result["ledger"])
        self.assert_safe(result)

    def test_duplicate_repair_id_is_rejected_on_append(self):
        ledger = build_repair_ledger(cycle_id="cycle-001", records=[self.record])
        duplicate = dict(
            self.record,
            before_sha="after456",
            after_sha="after789",
        )
        result = append_repair_to_ledger(ledger, duplicate)
        self.assertIn("duplicate_repair_id", result["reasons"])
        self.assert_safe(result)

    def test_sha_chain_mismatch_is_rejected_on_append(self):
        ledger = build_repair_ledger(cycle_id="cycle-001", records=[self.record])
        mismatched = dict(
            self.record,
            repair_id="repair-002",
            before_sha="unexpected",
            after_sha="after789",
        )
        result = append_repair_to_ledger(ledger, mismatched)
        self.assertIn("sha_chain_mismatch", result["reasons"])
        self.assert_safe(result)

    def test_even_valid_second_repair_is_rejected_by_cycle_limit(self):
        ledger = build_repair_ledger(cycle_id="cycle-001", records=[self.record])
        second = dict(
            self.record,
            repair_id="repair-002",
            before_sha="after456",
            after_sha="after789",
        )
        result = append_repair_to_ledger(ledger, second)
        self.assertIn("multiple_repairs_in_cycle", result["reasons"])
        self.assert_safe(result)

    def test_same_sha_is_rejected(self):
        record = dict(self.record, after_sha="before123")
        result = build_repair_ledger(cycle_id="cycle-001", records=[record])
        self.assertIn("sha_not_changed", result["reasons"])
        self.assert_safe(result)

    def test_nonterminal_validation_is_rejected(self):
        record = dict(self.record, validation_status="repair_validation_hold")
        result = build_repair_ledger(cycle_id="cycle-001", records=[record])
        self.assertIn("validation_not_terminal", result["reasons"])
        self.assert_safe(result)

    def test_empty_cycle_is_rejected(self):
        result = build_repair_ledger(cycle_id="cycle-001", records=[])
        self.assertIn("empty_cycle", result["reasons"])
        self.assert_safe(result)

    def test_non_research_scope_is_rejected(self):
        record = dict(self.record, scope="production")
        result = build_repair_ledger(cycle_id="cycle-001", records=[record])
        self.assertIn("scope_not_allowed", result["reasons"])
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
