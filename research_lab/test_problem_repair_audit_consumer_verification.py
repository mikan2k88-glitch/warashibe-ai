"""Regression tests for the consumer-facing audit verification contract."""
import unittest

from research_lab.problem_repair_audit_consumer_verification import (
    verify_audit_bundle_for_consumer,
)


class TestProblemRepairAuditConsumerVerification(unittest.TestCase):
    def test_verified_bundle_maps_to_accept(self):
        result = verify_audit_bundle_for_consumer(self._valid_bundle())
        self.assertEqual(result["status"], "audit_consumer_verified")
        self.assertEqual(result["decision"], "accept")
        self.assertTrue(result["integrity_verified"])
        self.assertEqual(result["target_sha"], "a" * 40)
        self.assertEqual(result["bundle_digest"], "b" * 64)
        self.assertEqual(result["reason_codes"], ())
        self.assert_safe(result)

    def test_tampered_bundle_maps_to_reject(self):
        bundle = self._valid_bundle()
        bundle["target_sha"] = "c" * 40
        result = verify_audit_bundle_for_consumer(bundle)
        self.assertEqual(result["status"], "audit_consumer_rejected")
        self.assertEqual(result["decision"], "reject")
        self.assertFalse(result["integrity_verified"])
        self.assertIn("embedded_package_target_sha_mismatch", result["reason_codes"])
        self.assert_safe(result)

    def test_malformed_bundle_maps_to_hold(self):
        result = verify_audit_bundle_for_consumer(None)
        self.assertEqual(result["status"], "audit_consumer_hold")
        self.assertEqual(result["decision"], "hold")
        self.assertFalse(result["integrity_verified"])
        self.assertIn("invalid_bundle", result["reason_codes"])
        self.assert_safe(result)

    def test_unknown_field_is_rejected_not_accepted(self):
        bundle = self._valid_bundle()
        bundle["unexpected"] = True
        result = verify_audit_bundle_for_consumer(bundle)
        self.assertEqual(result["decision"], "reject")
        self.assertIn("unexpected_bundle_field", result["reason_codes"])
        self.assert_safe(result)

    def test_result_schema_is_fixed_and_public_safe(self):
        result = verify_audit_bundle_for_consumer(None)
        self.assertEqual(
            set(result),
            {
                "consumer_schema_version",
                "status",
                "decision",
                "integrity_verified",
                "target_sha",
                "bundle_digest",
                "reason_codes",
                "read_only",
                "external_runtime_action_authorized",
                "auto_retry_authorized",
                "auto_rollback_authorized",
                "contains_secrets",
                "contains_internal_execution_details",
            },
        )
        self.assertFalse(result["contains_secrets"])
        self.assertFalse(result["contains_internal_execution_details"])
        self.assertTrue(result["read_only"])
        self.assert_safe(result)

    def assert_safe(self, result):
        self.assertFalse(result["external_runtime_action_authorized"])
        self.assertFalse(result["auto_retry_authorized"])
        self.assertFalse(result["auto_rollback_authorized"])

    def _valid_bundle(self):
        return {
            "bundle_schema_version": "1.0",
            "bundle_type": "warashibe-ai-public-repair-audit-distribution-bundle",
            "target_sha": "a" * 40,
            "package_schema_version": "1.0",
            "package_digest_algorithm": "sha256",
            "package_digest": "b" * 64,
            "artifact_name": "public-repair-audit-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.json",
            "artifact_id": "c" * 64,
            "package": {"target_sha": "a" * 40, "package_digest": "b" * 64},
            "metadata": {
                "target_sha": "a" * 40,
                "package_digest": "b" * 64,
                "artifact_id": "c" * 64,
                "artifact_name": "public-repair-audit-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.json",
            },
            "bundle_digest_algorithm": "sha256",
            "bundle_digest": "d" * 64,
        }


if __name__ == "__main__":
    unittest.main()
