"""Regression tests for deterministic repair history integrity digests."""
import unittest

from research_lab.problem_repair_history_digest import (
    build_repair_history_digest,
    verify_repair_history_digest,
)


class TestProblemRepairHistoryDigest(unittest.TestCase):
    def snapshot_result(self):
        return {
            "status": "repair_history_snapshot_ready",
            "snapshot": {
                "scope": "research-lab",
                "cycle_count": 2,
                "repair_count": 2,
                "success_count": 1,
                "failure_count": 1,
                "head_start": "sha-a",
                "head_end": "sha-c",
                "continuous": True,
                "cycles": (
                    {
                        "cycle_id": "c1",
                        "repair_id": "r1",
                        "head_before": "sha-a",
                        "head_after": "sha-b",
                        "validation_status": "repair_validated_success",
                    },
                    {
                        "cycle_id": "c2",
                        "repair_id": "r2",
                        "head_before": "sha-b",
                        "head_after": "sha-c",
                        "validation_status": "repair_validated_failure",
                    },
                ),
            },
        }

    def assert_safe(self, result):
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)

    def test_same_history_produces_same_digest(self):
        first = build_repair_history_digest(self.snapshot_result())
        second = build_repair_history_digest(self.snapshot_result())
        self.assertEqual(first["status"], "repair_history_digest_ready")
        self.assertEqual(first["digest"], second["digest"])
        self.assertEqual(len(first["digest"]), 64)
        self.assertIs(first["integrity_ready"], True)
        self.assert_safe(first)

    def test_dict_key_order_does_not_change_digest(self):
        original = self.snapshot_result()
        snapshot = original["snapshot"]
        reordered = {
            "status": "repair_history_snapshot_ready",
            "snapshot": {
                "cycles": snapshot["cycles"],
                "continuous": snapshot["continuous"],
                "head_end": snapshot["head_end"],
                "head_start": snapshot["head_start"],
                "failure_count": snapshot["failure_count"],
                "success_count": snapshot["success_count"],
                "repair_count": snapshot["repair_count"],
                "cycle_count": snapshot["cycle_count"],
                "scope": snapshot["scope"],
            },
        }
        self.assertEqual(
            build_repair_history_digest(original)["digest"],
            build_repair_history_digest(reordered)["digest"],
        )

    def test_one_field_change_changes_digest(self):
        original = self.snapshot_result()
        changed = self.snapshot_result()
        changed["snapshot"] = dict(changed["snapshot"], head_end="sha-d")
        first = build_repair_history_digest(original)
        second = build_repair_history_digest(changed)
        self.assertNotEqual(first["digest"], second["digest"])
        self.assert_safe(second)

    def test_matching_digest_verifies(self):
        snapshot = self.snapshot_result()
        digest = build_repair_history_digest(snapshot)["digest"]
        result = verify_repair_history_digest(snapshot, digest)
        self.assertEqual(result["status"], "repair_history_integrity_verified")
        self.assertIs(result["integrity_verified"], True)
        self.assertEqual(result["observed_digest"], digest)
        self.assert_safe(result)

    def test_tampered_history_is_detected(self):
        original = self.snapshot_result()
        digest = build_repair_history_digest(original)["digest"]
        changed = self.snapshot_result()
        changed["snapshot"] = dict(changed["snapshot"], success_count=2)
        result = verify_repair_history_digest(changed, digest)
        self.assertEqual(result["status"], "repair_history_integrity_mismatch")
        self.assertIs(result["integrity_verified"], False)
        self.assertIn("digest_mismatch", result["reasons"])
        self.assert_safe(result)

    def test_unready_snapshot_is_rejected(self):
        result = build_repair_history_digest({"status": "hold_repair_history_snapshot"})
        self.assertIn("snapshot_not_ready", result["reasons"])
        self.assert_safe(result)

    def test_noncontinuous_snapshot_is_rejected(self):
        snapshot = self.snapshot_result()
        snapshot["snapshot"] = dict(snapshot["snapshot"], continuous=False)
        result = build_repair_history_digest(snapshot)
        self.assertIn("continuity_not_confirmed", result["reasons"])
        self.assert_safe(result)

    def test_invalid_expected_digest_is_rejected(self):
        result = verify_repair_history_digest(self.snapshot_result(), "bad")
        self.assertIn("invalid_expected_digest", result["reasons"])
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
