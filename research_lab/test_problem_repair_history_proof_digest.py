"""Regression tests for deterministic repair-history CI proof digests."""
import unittest

from research_lab.problem_repair_history_proof_digest import (
    build_repair_history_proof_digest,
    verify_repair_history_proof_digest,
)


class TestProblemRepairHistoryProofDigest(unittest.TestCase):
    def proof_result(self):
        return {
            "status": "repair_history_ci_proof_ready",
            "proof": {
                "scope": "research-lab",
                "history_digest_algorithm": "sha256",
                "history_digest": "a" * 64,
                "run_id": 123456,
                "run_number": 930,
                "head_sha": "sha-abc",
                "ci_status": "completed",
                "ci_conclusion": "success",
                "exact_sha_verified": True,
            },
        }

    def assert_safe(self, result):
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)

    def test_same_proof_produces_same_digest(self):
        first = build_repair_history_proof_digest(self.proof_result())
        second = build_repair_history_proof_digest(self.proof_result())
        self.assertEqual(first["status"], "repair_history_proof_digest_ready")
        self.assertEqual(first["proof_digest"], second["proof_digest"])
        self.assertEqual(len(first["proof_digest"]), 64)
        self.assertIs(first["integrity_ready"], True)
        self.assert_safe(first)

    def test_key_order_does_not_change_digest(self):
        original = self.proof_result()
        proof = original["proof"]
        reordered = {
            "status": "repair_history_ci_proof_ready",
            "proof": {
                "exact_sha_verified": proof["exact_sha_verified"],
                "ci_conclusion": proof["ci_conclusion"],
                "ci_status": proof["ci_status"],
                "head_sha": proof["head_sha"],
                "run_number": proof["run_number"],
                "run_id": proof["run_id"],
                "history_digest": proof["history_digest"],
                "history_digest_algorithm": proof["history_digest_algorithm"],
                "scope": proof["scope"],
            },
        }
        self.assertEqual(
            build_repair_history_proof_digest(original)["proof_digest"],
            build_repair_history_proof_digest(reordered)["proof_digest"],
        )

    def test_one_field_change_changes_digest(self):
        original = self.proof_result()
        changed = self.proof_result()
        changed["proof"] = dict(changed["proof"], run_number=931)
        first = build_repair_history_proof_digest(original)
        second = build_repair_history_proof_digest(changed)
        self.assertNotEqual(first["proof_digest"], second["proof_digest"])
        self.assert_safe(second)

    def test_matching_digest_verifies(self):
        proof = self.proof_result()
        digest = build_repair_history_proof_digest(proof)["proof_digest"]
        result = verify_repair_history_proof_digest(proof, digest)
        self.assertEqual(result["status"], "repair_history_proof_integrity_verified")
        self.assertIs(result["integrity_verified"], True)
        self.assertEqual(result["observed_digest"], digest)
        self.assert_safe(result)

    def test_tampered_proof_is_detected(self):
        original = self.proof_result()
        digest = build_repair_history_proof_digest(original)["proof_digest"]
        changed = self.proof_result()
        changed["proof"] = dict(changed["proof"], head_sha="sha-def")
        result = verify_repair_history_proof_digest(changed, digest)
        self.assertEqual(result["status"], "repair_history_proof_integrity_mismatch")
        self.assertIs(result["integrity_verified"], False)
        self.assertIn("proof_digest_mismatch", result["reasons"])
        self.assert_safe(result)

    def test_unready_proof_is_rejected(self):
        result = build_repair_history_proof_digest({"status": "hold_repair_history_ci_proof"})
        self.assertIn("proof_not_ready", result["reasons"])
        self.assert_safe(result)

    def test_unsuccessful_ci_evidence_is_rejected(self):
        proof = self.proof_result()
        proof["proof"] = dict(proof["proof"], ci_conclusion="failure")
        result = build_repair_history_proof_digest(proof)
        self.assertIn("ci_evidence_not_successful", result["reasons"])
        self.assert_safe(result)

    def test_invalid_expected_digest_is_rejected(self):
        result = verify_repair_history_proof_digest(self.proof_result(), "bad")
        self.assertIn("invalid_expected_digest", result["reasons"])
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
