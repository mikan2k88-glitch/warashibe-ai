"""Regression tests for the public repair audit distribution package."""
import unittest

from research_lab.problem_repair_public_audit_package import (
    build_public_repair_audit_package,
    verify_public_repair_audit_package,
)


class TestProblemRepairPublicAuditPackage(unittest.TestCase):
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

    def test_package_contains_summary_digest_and_target_sha(self):
        result = build_public_repair_audit_package(self.summary_result())
        self.assertEqual(result["status"], "public_repair_audit_package_ready")
        self.assertIs(result["integrity_ready"], True)
        package = result["package"]
        self.assertEqual(package["package_schema_version"], "1.0")
        self.assertEqual(package["package_type"], "warashibe-ai-public-repair-audit")
        self.assertEqual(package["target_sha"], "sha-final")
        self.assertEqual(package["summary_digest_algorithm"], "sha256")
        self.assertEqual(len(package["summary_digest"]), 64)
        self.assertEqual(package["package_digest_algorithm"], "sha256")
        self.assertEqual(len(package["package_digest"]), 64)
        self.assertEqual(package["summary"]["target_sha"], "sha-final")
        self.assert_safe(result)

    def test_package_uses_exact_fixed_field_set(self):
        package = build_public_repair_audit_package(self.summary_result())["package"]
        self.assertEqual(
            set(package),
            {
                "package_schema_version",
                "package_type",
                "target_sha",
                "summary_digest_algorithm",
                "summary_digest",
                "package_digest_algorithm",
                "summary",
                "package_digest",
            },
        )

    def test_same_summary_produces_same_package_digest(self):
        first = build_public_repair_audit_package(self.summary_result())
        second = build_public_repair_audit_package(self.summary_result())
        self.assertEqual(first["package"]["summary_digest"], second["package"]["summary_digest"])
        self.assertEqual(first["package"]["package_digest"], second["package"]["package_digest"])
        self.assert_safe(first)

    def test_package_verifies_from_single_object(self):
        built = build_public_repair_audit_package(self.summary_result())
        result = verify_public_repair_audit_package(built["package"])
        self.assertEqual(result["status"], "public_repair_audit_package_verified")
        self.assertIs(result["integrity_verified"], True)
        self.assertEqual(result["target_sha"], "sha-final")
        self.assert_safe(result)

    def test_summary_tampering_is_detected(self):
        built = build_public_repair_audit_package(self.summary_result())
        package = dict(built["package"])
        package["summary"] = dict(package["summary"], verification_status="unverified")
        result = verify_public_repair_audit_package(package)
        self.assertEqual(result["status"], "public_repair_audit_package_mismatch")
        self.assertIn("summary_digest_mismatch", result["reasons"])
        self.assert_safe(result)

    def test_target_sha_mismatch_is_detected(self):
        built = build_public_repair_audit_package(self.summary_result())
        package = dict(built["package"], target_sha="sha-other")
        result = verify_public_repair_audit_package(package)
        self.assertEqual(result["status"], "public_repair_audit_package_mismatch")
        self.assertIn("target_sha_mismatch", result["reasons"])
        self.assert_safe(result)

    def test_package_digest_tampering_is_detected(self):
        built = build_public_repair_audit_package(self.summary_result())
        package = dict(built["package"], package_digest="b" * 64)
        result = verify_public_repair_audit_package(package)
        self.assertEqual(result["status"], "public_repair_audit_package_mismatch")
        self.assertIn("package_digest_mismatch", result["reasons"])
        self.assert_safe(result)

    def test_unknown_package_field_is_rejected(self):
        built = build_public_repair_audit_package(self.summary_result())
        package = dict(built["package"], unexpected_field="must-not-be-accepted")
        result = verify_public_repair_audit_package(package)
        self.assertIn("unexpected_package_field", result["reasons"])
        self.assert_safe(result)

    def test_missing_package_field_is_rejected(self):
        built = build_public_repair_audit_package(self.summary_result())
        package = dict(built["package"])
        package.pop("summary_digest")
        result = verify_public_repair_audit_package(package)
        self.assertIn("missing_package_field", result["reasons"])
        self.assert_safe(result)

    def test_wrong_package_schema_is_rejected(self):
        built = build_public_repair_audit_package(self.summary_result())
        package = dict(built["package"], package_schema_version="2.0")
        result = verify_public_repair_audit_package(package)
        self.assertIn("package_schema_version_not_supported", result["reasons"])
        self.assert_safe(result)

    def test_non_public_summary_is_rejected(self):
        summary = self.summary_result()
        summary["public_safe"] = False
        result = build_public_repair_audit_package(summary)
        self.assertIn("summary_not_public_safe", result["reasons"])
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
