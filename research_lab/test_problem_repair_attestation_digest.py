"""Regression tests for final attestation integrity digests."""
import unittest

from research_lab.problem_repair_attestation_digest import (
    build_repair_attestation_digest,
    verify_repair_attestation_digest,
)


class TestProblemRepairAttestationDigest(unittest.TestCase):
    def attestation_result(self):
        return {
            "status": "repair_attestation_ready",
            "attestation": {
                "schema_version": "1.0",
                "scope": "research-lab",
                "target_sha": "sha-final",
                "history_digest_algorithm": "sha256",
                "history_digest": "a" * 64,
                "proof_digest_algorithm": "sha256",
                "proof_digest": "b" * 64,
                "history_integrity_ready": True,
                "ci_proof_integrity_ready": True,
                "exact_sha_required": True,
                "verified": True,
            },
        }

    def assert_safe(self, result):
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)

    def test_same_attestation_produces_same_digest(self):
        first = build_repair_attestation_digest(self.attestation_result())
        second = build_repair_attestation_digest(self.attestation_result())
        self.assertEqual(first["status"], "repair_attestation_digest_ready")
        self.assertEqual(first["attestation_digest"], second["attestation_digest"])
        self.assertEqual(len(first["attestation_digest"]), 64)
        self.assertIs(first["integrity_ready"], True)
        self.assert_safe(first)

    def test_key_order_does_not_change_digest(self):
        original = self.attestation_result()
        att = original["attestation"]
        reordered = {
            "status": "repair_attestation_ready",
            "attestation": {
                "verified": att["verified"],
                "exact_sha_required": att["exact_sha_required"],
                "ci_proof_integrity_ready": att["ci_proof_integrity_ready"],
                "history_integrity_ready": att["history_integrity_ready"],
                "proof_digest": att["proof_digest"],
                "proof_digest_algorithm": att["proof_digest_algorithm"],
                "history_digest": att["history_digest"],
                "history_digest_algorithm": att["history_digest_algorithm"],
                "target_sha": att["target_sha"],
                "scope": att["scope"],
                "schema_version": att["schema_version"],
            },
        }
        self.assertEqual(
            build_repair_attestation_digest(original)["attestation_digest"],
            build_repair_attestation_digest(reordered)["attestation_digest"],
        )

    def test_one_field_change_changes_digest(self):
        original = self.attestation_result()
        changed = self.attestation_result()
        changed["attestation"] = dict(changed["attestation"], target_sha="sha-other")
        first = build_repair_attestation_digest(original)
        second = build_repair_attestation_digest(changed)
        self.assertNotEqual(first["attestation_digest"], second["attestation_digest"])
        self.assert_safe(second)

    def test_matching_digest_verifies(self):
        attestation = self.attestation_result()
        digest = build_repair_attestation_digest(attestation)["attestation_digest"]
        result = verify_repair_attestation_digest(attestation, digest)
        self.assertEqual(result["status"], "repair_attestation_integrity_verified")
        self.assertIs(result["integrity_verified"], True)
        self.assertEqual(result["observed_digest"], digest)
        self.assert_safe(result)

    def test_tampering_is_detected(self):
        original = self.attestation_result()
        digest = build_repair_attestation_digest(original)["attestation_digest"]
        changed = self.attestation_result()
        changed["attestation"] = dict(changed["attestation"], proof_digest="c" * 64)
        result = verify_repair_attestation_digest(changed, digest)
        self.assertEqual(result["status"], "repair_attestation_integrity_mismatch")
        self.assertIs(result["integrity_verified"], False)
        self.assertIn("attestation_digest_mismatch", result["reasons"])
        self.assert_safe(result)

    def test_unready_attestation_is_rejected(self):
        result = build_repair_attestation_digest({"status": "hold_repair_attestation"})
        self.assertIn("attestation_not_ready", result["reasons"])
        self.assert_safe(result)

    def test_unverified_attestation_is_rejected(self):
        attestation = self.attestation_result()
        attestation["attestation"] = dict(attestation["attestation"], verified=False)
        result = build_repair_attestation_digest(attestation)
        self.assertIn("attestation_not_verified", result["reasons"])
        self.assert_safe(result)

    def test_invalid_expected_digest_is_rejected(self):
        result = verify_repair_attestation_digest(self.attestation_result(), "bad")
        self.assertIn("invalid_expected_digest", result["reasons"])
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
