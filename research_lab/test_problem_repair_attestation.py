"""Regression tests for final repair attestation envelopes."""
import unittest

from research_lab.problem_repair_attestation import build_repair_attestation_envelope


class TestProblemRepairAttestation(unittest.TestCase):
    def history_digest_result(self, digest="a" * 64):
        return {
            "status": "repair_history_digest_ready",
            "digest": digest,
            "integrity_ready": True,
        }

    def proof_digest_result(self, digest="b" * 64):
        return {
            "status": "repair_history_proof_digest_ready",
            "proof_digest": digest,
            "integrity_ready": True,
        }

    def assert_safe(self, result):
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)

    def test_valid_digests_build_self_contained_attestation(self):
        result = build_repair_attestation_envelope(
            history_digest_result=self.history_digest_result(),
            proof_digest_result=self.proof_digest_result(),
            target_sha="sha-final",
        )
        self.assertEqual(result["status"], "repair_attestation_ready")
        self.assertIs(result["attestation_ready"], True)
        attestation = result["attestation"]
        self.assertEqual(attestation["schema_version"], "1.0")
        self.assertEqual(attestation["scope"], "research-lab")
        self.assertEqual(attestation["target_sha"], "sha-final")
        self.assertEqual(attestation["history_digest"], "a" * 64)
        self.assertEqual(attestation["proof_digest"], "b" * 64)
        self.assertIs(attestation["history_integrity_ready"], True)
        self.assertIs(attestation["ci_proof_integrity_ready"], True)
        self.assertIs(attestation["exact_sha_required"], True)
        self.assertIs(attestation["verified"], True)
        self.assert_safe(result)

    def test_unready_history_digest_is_rejected(self):
        result = build_repair_attestation_envelope(
            history_digest_result={"status": "hold_repair_history_digest"},
            proof_digest_result=self.proof_digest_result(),
            target_sha="sha-final",
        )
        self.assertIn("history_digest_not_ready", result["reasons"])
        self.assertIsNone(result["attestation"])
        self.assert_safe(result)

    def test_unready_proof_digest_is_rejected(self):
        result = build_repair_attestation_envelope(
            history_digest_result=self.history_digest_result(),
            proof_digest_result={"status": "hold_repair_history_proof_digest"},
            target_sha="sha-final",
        )
        self.assertIn("proof_digest_not_ready", result["reasons"])
        self.assert_safe(result)

    def test_invalid_history_digest_is_rejected(self):
        result = build_repair_attestation_envelope(
            history_digest_result=self.history_digest_result("short"),
            proof_digest_result=self.proof_digest_result(),
            target_sha="sha-final",
        )
        self.assertIn("invalid_history_digest", result["reasons"])
        self.assert_safe(result)

    def test_invalid_proof_digest_is_rejected(self):
        result = build_repair_attestation_envelope(
            history_digest_result=self.history_digest_result(),
            proof_digest_result=self.proof_digest_result("short"),
            target_sha="sha-final",
        )
        self.assertIn("invalid_proof_digest", result["reasons"])
        self.assert_safe(result)

    def test_blank_target_sha_is_rejected(self):
        result = build_repair_attestation_envelope(
            history_digest_result=self.history_digest_result(),
            proof_digest_result=self.proof_digest_result(),
            target_sha=" ",
        )
        self.assertIn("invalid_target_sha", result["reasons"])
        self.assert_safe(result)

    def test_schema_version_is_fixed(self):
        result = build_repair_attestation_envelope(
            history_digest_result=self.history_digest_result(),
            proof_digest_result=self.proof_digest_result(),
            target_sha="sha-final",
        )
        self.assertEqual(result["schema_version"], "1.0")
        self.assertEqual(result["attestation"]["schema_version"], "1.0")
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
