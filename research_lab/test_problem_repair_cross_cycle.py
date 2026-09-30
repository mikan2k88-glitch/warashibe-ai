"""Regression tests for cross-cycle repair continuity."""
import unittest

from research_lab.problem_repair_cross_cycle import validate_cross_cycle_continuity


class TestProblemRepairCrossCycle(unittest.TestCase):
    def ledger(self, *, cycle_id, repair_id, before_sha, after_sha):
        return {
            "cycle_id": cycle_id,
            "repair_ids": (repair_id,),
            "head_before": before_sha,
            "head_after": after_sha,
            "scope": "research-lab",
            "single_repair_cycle": True,
            "repair_count": 1,
        }

    def assert_safe(self, result):
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)

    def test_two_cycles_with_continuous_sha_chain_pass(self):
        result = validate_cross_cycle_continuity([
            self.ledger(
                cycle_id="cycle-001",
                repair_id="repair-001",
                before_sha="sha-a",
                after_sha="sha-b",
            ),
            self.ledger(
                cycle_id="cycle-002",
                repair_id="repair-002",
                before_sha="sha-b",
                after_sha="sha-c",
            ),
        ])
        self.assertEqual(result["status"], "cross_cycle_continuity_ok")
        self.assertIs(result["continuous"], True)
        self.assertEqual(result["checked_cycles"], 2)
        self.assert_safe(result)

    def test_three_cycle_chain_passes(self):
        result = validate_cross_cycle_continuity([
            self.ledger(cycle_id="c1", repair_id="r1", before_sha="a", after_sha="b"),
            self.ledger(cycle_id="c2", repair_id="r2", before_sha="b", after_sha="c"),
            self.ledger(cycle_id="c3", repair_id="r3", before_sha="c", after_sha="d"),
        ])
        self.assertEqual(result["status"], "cross_cycle_continuity_ok")
        self.assertEqual(result["checked_cycles"], 3)
        self.assert_safe(result)

    def test_gap_or_branch_is_rejected(self):
        result = validate_cross_cycle_continuity([
            self.ledger(cycle_id="c1", repair_id="r1", before_sha="a", after_sha="b"),
            self.ledger(cycle_id="c2", repair_id="r2", before_sha="x", after_sha="y"),
        ])
        self.assertIn("sha_chain_mismatch", result["reasons"])
        self.assertIs(result["continuous"], False)
        self.assert_safe(result)

    def test_duplicate_cycle_id_is_rejected(self):
        result = validate_cross_cycle_continuity([
            self.ledger(cycle_id="same", repair_id="r1", before_sha="a", after_sha="b"),
            self.ledger(cycle_id="same", repair_id="r2", before_sha="b", after_sha="c"),
        ])
        self.assertIn("duplicate_cycle_id", result["reasons"])
        self.assert_safe(result)

    def test_duplicate_repair_id_is_rejected(self):
        result = validate_cross_cycle_continuity([
            self.ledger(cycle_id="c1", repair_id="same", before_sha="a", after_sha="b"),
            self.ledger(cycle_id="c2", repair_id="same", before_sha="b", after_sha="c"),
        ])
        self.assertIn("duplicate_repair_id", result["reasons"])
        self.assert_safe(result)

    def test_self_linked_cycle_is_rejected(self):
        result = validate_cross_cycle_continuity([
            self.ledger(cycle_id="c1", repair_id="r1", before_sha="a", after_sha="a"),
            self.ledger(cycle_id="c2", repair_id="r2", before_sha="a", after_sha="b"),
        ])
        self.assertIn("self_linked_cycle", result["reasons"])
        self.assert_safe(result)

    def test_non_research_scope_is_rejected(self):
        bad = self.ledger(cycle_id="c1", repair_id="r1", before_sha="a", after_sha="b")
        bad["scope"] = "production"
        result = validate_cross_cycle_continuity([
            bad,
            self.ledger(cycle_id="c2", repair_id="r2", before_sha="b", after_sha="c"),
        ])
        self.assertIn("scope_not_allowed", result["reasons"])
        self.assert_safe(result)

    def test_more_than_one_repair_id_per_cycle_is_rejected(self):
        bad = self.ledger(cycle_id="c1", repair_id="r1", before_sha="a", after_sha="b")
        bad["repair_ids"] = ("r1", "r2")
        result = validate_cross_cycle_continuity([
            bad,
            self.ledger(cycle_id="c2", repair_id="r3", before_sha="b", after_sha="c"),
        ])
        self.assertIn("repair_count_not_one", result["reasons"])
        self.assert_safe(result)

    def test_less_than_two_cycles_is_rejected(self):
        result = validate_cross_cycle_continuity([
            self.ledger(cycle_id="c1", repair_id="r1", before_sha="a", after_sha="b"),
        ])
        self.assertIn("insufficient_cycles", result["reasons"])
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
