"""Regression tests for repair-history CI proof records."""
import unittest

from research_lab.problem_repair_history_ci_proof import build_repair_history_ci_proof


class TestProblemRepairHistoryCIProof(unittest.TestCase):
    def digest_result(self, digest="a" * 64):
        return {
            "status": "repair_history_digest_ready",
            "digest_algorithm": "sha256",
            "digest": digest,
            "integrity_ready": True,
        }

    def assert_safe(self, result):
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)

    def test_exact_sha_success_builds_proof(self):
        result = build_repair_history_ci_proof(
            digest_result=self.digest_result(),
            run_id=123456,
            run_number=927,
            expected_head_sha="sha-abc",
            observed_head_sha="sha-abc",
            ci_status="completed",
            ci_conclusion="success",
        )
        self.assertEqual(result["status"], "repair_history_ci_proof_ready")
        self.assertIs(result["proof_ready"], True)
        proof = result["proof"]
        self.assertEqual(proof["history_digest"], "a" * 64)
        self.assertEqual(proof["run_id"], 123456)
        self.assertEqual(proof["run_number"], 927)
        self.assertEqual(proof["head_sha"], "sha-abc")
        self.assertIs(proof["exact_sha_verified"], True)
        self.assert_safe(result)

    def test_sha_mismatch_is_rejected(self):
        result = build_repair_history_ci_proof(
            digest_result=self.digest_result(),
            run_id=1,
            run_number=1,
            expected_head_sha="sha-a",
            observed_head_sha="sha-b",
            ci_status="completed",
            ci_conclusion="success",
        )
        self.assertIn("head_sha_mismatch", result["reasons"])
        self.assertIsNone(result["proof"])
        self.assert_safe(result)

    def test_incomplete_ci_is_rejected(self):
        result = build_repair_history_ci_proof(
            digest_result=self.digest_result(),
            run_id=1,
            run_number=1,
            expected_head_sha="sha-a",
            observed_head_sha="sha-a",
            ci_status="in_progress",
            ci_conclusion="success",
        )
        self.assertIn("ci_not_completed", result["reasons"])
        self.assert_safe(result)

    def test_failed_ci_is_rejected(self):
        result = build_repair_history_ci_proof(
            digest_result=self.digest_result(),
            run_id=1,
            run_number=1,
            expected_head_sha="sha-a",
            observed_head_sha="sha-a",
            ci_status="completed",
            ci_conclusion="failure",
        )
        self.assertIn("ci_failure", result["reasons"])
        self.assert_safe(result)

    def test_unready_digest_is_rejected(self):
        result = build_repair_history_ci_proof(
            digest_result={"status": "hold_repair_history_digest"},
            run_id=1,
            run_number=1,
            expected_head_sha="sha-a",
            observed_head_sha="sha-a",
            ci_status="completed",
            ci_conclusion="success",
        )
        self.assertIn("digest_not_ready", result["reasons"])
        self.assert_safe(result)

    def test_invalid_run_metadata_is_rejected(self):
        result = build_repair_history_ci_proof(
            digest_result=self.digest_result(),
            run_id=0,
            run_number=1,
            expected_head_sha="sha-a",
            observed_head_sha="sha-a",
            ci_status="completed",
            ci_conclusion="success",
        )
        self.assertIn("invalid_run_id", result["reasons"])
        self.assert_safe(result)

    def test_invalid_digest_is_rejected(self):
        result = build_repair_history_ci_proof(
            digest_result=self.digest_result("short"),
            run_id=1,
            run_number=1,
            expected_head_sha="sha-a",
            observed_head_sha="sha-a",
            ci_status="completed",
            ci_conclusion="success",
        )
        self.assertIn("invalid_digest", result["reasons"])
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
