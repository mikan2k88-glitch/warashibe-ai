"""Regression tests for public-safe repair audit summaries."""
import unittest

from research_lab.problem_repair_public_audit_summary import (
    build_public_repair_audit_summary,
)


class TestProblemRepairPublicAuditSummary(unittest.TestCase):
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

    def attestation_digest_result(self):
        return {
            "status": "repair_attestation_digest_ready",
            "attestation_digest": "c" * 64,
            "integrity_ready": True,
        }

    def assert_safe(self, result):
        self.assertIs(result["read_only"], True)
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)

    def test_verified_attestation_builds_minimal_public_summary(self):
        result = build_public_repair_audit_summary(
            attestation_result=self.attestation_result(),
            attestation_digest_result=self.attestation_digest_result(),
        )
        self.assertEqual(result["status"], "public_repair_audit_summary_ready")
        self.assertIs(result["public_safe"], True)
        summary = result["summary"]
        self.assertEqual(summary["schema_version"], "1.0")
        self.assertEqual(summary["scope"], "research-lab")
        self.assertEqual(summary["target_sha"], "sha-final")
        self.assertEqual(summary["verification_status"], "verified")
        self.assertEqual(summary["integrity_status"], "verified")
        self.assertEqual(summary["attestation_digest"], "c" * 64)
        self.assertIs(summary["read_only"], True)
        self.assertIs(summary["contains_secrets"], False)
        self.assertIs(summary["contains_internal_execution_details"], False)
        self.assertNotIn("history_digest", summary)
        self.assertNotIn("proof_digest", summary)
        self.assertNotIn("canonical_payload", summary)
        self.assert_safe(result)

    def test_unready_attestation_is_rejected(self):
        result = build_public_repair_audit_summary(
            attestation_result={"status": "hold_repair_attestation"},
            attestation_digest_result=self.attestation_digest_result(),
        )
        self.assertIn("attestation_not_ready", result["reasons"])
        self.assert_safe(result)

    def test_unready_attestation_digest_is_rejected(self):
        result = build_public_repair_audit_summary(
            attestation_result=self.attestation_result(),
            attestation_digest_result={"status": "hold_repair_attestation_digest"},
        )
        self.assertIn("attestation_digest_not_ready", result["reasons"])
        self.assert_safe(result)

    def test_unverified_attestation_is_rejected(self):
        attestation = self.attestation_result()
        attestation["attestation"] = dict(attestation["attestation"], verified=False)
        result = build_public_repair_audit_summary(
            attestation_result=attestation,
            attestation_digest_result=self.attestation_digest_result(),
        )
        self.assertIn("attestation_not_verified", result["reasons"])
        self.assert_safe(result)

    def test_nonresearch_scope_is_rejected(self):
        attestation = self.attestation_result()
        attestation["attestation"] = dict(attestation["attestation"], scope="production")
        result = build_public_repair_audit_summary(
            attestation_result=attestation,
            attestation_digest_result=self.attestation_digest_result(),
        )
        self.assertIn("scope_not_allowed", result["reasons"])
        self.assert_safe(result)

    def test_invalid_digest_is_rejected(self):
        digest_result = self.attestation_digest_result()
        digest_result["attestation_digest"] = "short"
        result = build_public_repair_audit_summary(
            attestation_result=self.attestation_result(),
            attestation_digest_result=digest_result,
        )
        self.assertIn("invalid_attestation_digest", result["reasons"])
        self.assert_safe(result)

    def test_blank_target_sha_is_rejected(self):
        attestation = self.attestation_result()
        attestation["attestation"] = dict(attestation["attestation"], target_sha=" ")
        result = build_public_repair_audit_summary(
            attestation_result=attestation,
            attestation_digest_result=self.attestation_digest_result(),
        )
        self.assertIn("invalid_target_sha", result["reasons"])
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
