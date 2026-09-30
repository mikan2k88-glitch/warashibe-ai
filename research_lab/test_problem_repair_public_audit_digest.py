"""Regression tests for public audit summary integrity digests."""
import unittest

from research_lab.problem_repair_public_audit_digest import (
    build_public_repair_audit_digest,
    verify_public_repair_audit_digest,
)


class TestProblemRepairPublicAuditDigest(unittest.TestCase):
    def summary_result(self):
        return {
            "status": "public_repair_audit_summary_ready",
            "public_safe": True,
            "read_only": True,
            "summary": {
                "schema_version": "1.0",
                "scope": "research-lab",
                "target_sha": "sha-final",
                "verification_status": "verified",
                "integrity_status": "verified",
                "attestation_digest_algorithm": "sha256",
                "attestation_digest": "a" * 64,
                "read_only": True,
                "contains_secrets": False,
                "contains_internal_execution_details": False,
            },
        }

    def assert_safe(self, result):
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)

    def test_same_summary_produces_same_digest(self):
        first = build_public_repair_audit_digest(self.summary_result())
        second = build_public_repair_audit_digest(self.summary_result())
        self.assertEqual(first["status"], "public_repair_audit_digest_ready")
        self.assertEqual(first["public_summary_digest"], second["public_summary_digest"])
        self.assertEqual(len(first["public_summary_digest"]), 64)
        self.assertIs(first["integrity_ready"], True)
        self.assert_safe(first)

    def test_key_order_does_not_change_digest(self):
        original = self.summary_result()
        summary = original["summary"]
        reordered = {
            "status": "public_repair_audit_summary_ready",
            "public_safe": True,
            "read_only": True,
            "summary": {
                "contains_internal_execution_details": summary["contains_internal_execution_details"],
                "contains_secrets": summary["contains_secrets"],
                "read_only": summary["read_only"],
                "attestation_digest": summary["attestation_digest"],
                "attestation_digest_algorithm": summary["attestation_digest_algorithm"],
                "integrity_status": summary["integrity_status"],
                "verification_status": summary["verification_status"],
                "target_sha": summary["target_sha"],
                "scope": summary["scope"],
                "schema_version": summary["schema_version"],
            },
        }
        self.assertEqual(
            build_public_repair_audit_digest(original)["public_summary_digest"],
            build_public_repair_audit_digest(reordered)["public_summary_digest"],
        )

    def test_one_field_change_changes_digest(self):
        original = self.summary_result()
        changed = self.summary_result()
        changed["summary"] = dict(changed["summary"], target_sha="sha-other")
        first = build_public_repair_audit_digest(original)
        second = build_public_repair_audit_digest(changed)
        self.assertNotEqual(first["public_summary_digest"], second["public_summary_digest"])
        self.assert_safe(second)

    def test_matching_digest_verifies(self):
        summary = self.summary_result()
        digest = build_public_repair_audit_digest(summary)["public_summary_digest"]
        result = verify_public_repair_audit_digest(summary, digest)
        self.assertEqual(result["status"], "public_repair_audit_integrity_verified")
        self.assertIs(result["integrity_verified"], True)
        self.assertEqual(result["observed_digest"], digest)
        self.assert_safe(result)

    def test_tampering_is_detected(self):
        original = self.summary_result()
        digest = build_public_repair_audit_digest(original)["public_summary_digest"]
        changed = self.summary_result()
        changed["summary"] = dict(changed["summary"], attestation_digest="b" * 64)
        result = verify_public_repair_audit_digest(changed, digest)
        self.assertEqual(result["status"], "public_repair_audit_integrity_mismatch")
        self.assertIs(result["integrity_verified"], False)
        self.assertIn("public_summary_digest_mismatch", result["reasons"])
        self.assert_safe(result)

    def test_unready_summary_is_rejected(self):
        result = build_public_repair_audit_digest({"status": "hold_public_repair_audit_summary"})
        self.assertIn("summary_not_ready", result["reasons"])
        self.assert_safe(result)

    def test_non_public_safe_summary_is_rejected(self):
        summary = self.summary_result()
        summary["public_safe"] = False
        result = build_public_repair_audit_digest(summary)
        self.assertIn("summary_not_public_safe", result["reasons"])
        self.assert_safe(result)

    def test_secret_flag_true_is_rejected(self):
        summary = self.summary_result()
        summary["summary"] = dict(summary["summary"], contains_secrets=True)
        result = build_public_repair_audit_digest(summary)
        self.assertIn("summary_secret_flag_invalid", result["reasons"])
        self.assert_safe(result)

    def test_invalid_expected_digest_is_rejected(self):
        result = verify_public_repair_audit_digest(self.summary_result(), "bad")
        self.assertIn("invalid_expected_digest", result["reasons"])
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
