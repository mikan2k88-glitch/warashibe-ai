"""Regression tests for the public audit distribution metadata contract."""
import unittest

from research_lab.problem_repair_audit_distribution_metadata import (
    build_audit_distribution_metadata,
    verify_audit_distribution_metadata,
)


class TestProblemRepairAuditDistributionMetadata(unittest.TestCase):
    def package_result(self):
        return {
            "status": "public_repair_audit_package_ready",
            "integrity_ready": True,
            "package": {
                "package_schema_version": "1.0",
                "package_type": "warashibe-ai-public-repair-audit",
                "target_sha": "a" * 40,
                "summary_digest_algorithm": "sha256",
                "summary_digest": "b" * 64,
                "package_digest_algorithm": "sha256",
                "summary": {
                    "schema_version": "1.0",
                    "scope": "research-lab",
                    "target_sha": "a" * 40,
                    "verification_status": "verified",
                    "integrity_status": "verified",
                    "attestation_digest_algorithm": "sha256",
                    "attestation_digest": "c" * 64,
                    "read_only": True,
                    "contains_secrets": False,
                    "contains_internal_execution_details": False,
                },
                "package_digest": "d" * 64,
            },
        }

    def assert_safe(self, result):
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)

    def test_builds_fixed_distribution_metadata(self):
        result = build_audit_distribution_metadata(
            package_result=self.package_result(),
            artifact_name="public-repair-audit-a" + "a" * 40 + ".json",
            generated_at="2026-09-30T00:00:00Z",
        )
        self.assertEqual(result["status"], "audit_distribution_metadata_ready")
        metadata = result["metadata"]
        self.assertEqual(
            set(metadata),
            {
                "metadata_schema_version",
                "metadata_type",
                "artifact_name",
                "generated_at",
                "target_sha",
                "package_schema_version",
                "package_digest_algorithm",
                "package_digest",
                "artifact_id",
            },
        )
        self.assertEqual(metadata["metadata_schema_version"], "1.0")
        self.assertEqual(metadata["metadata_type"], "warashibe-ai-public-repair-audit-distribution")
        self.assertEqual(metadata["target_sha"], "a" * 40)
        self.assertEqual(metadata["package_digest"], "d" * 64)
        self.assertEqual(len(metadata["artifact_id"]), 64)
        self.assert_safe(result)

    def test_same_inputs_produce_same_metadata(self):
        kwargs = {
            "package_result": self.package_result(),
            "artifact_name": "public-repair-audit-a" + "a" * 40 + ".json",
            "generated_at": "2026-09-30T00:00:00Z",
        }
        first = build_audit_distribution_metadata(**kwargs)
        second = build_audit_distribution_metadata(**kwargs)
        self.assertEqual(first["metadata"], second["metadata"])

    def test_invalid_generated_at_is_rejected(self):
        result = build_audit_distribution_metadata(
            package_result=self.package_result(),
            artifact_name="public-repair-audit-a" + "a" * 40 + ".json",
            generated_at="not-a-time",
        )
        self.assertIn("invalid_generated_at", result["reasons"])
        self.assert_safe(result)

    def test_invalid_artifact_name_is_rejected(self):
        result = build_audit_distribution_metadata(
            package_result=self.package_result(),
            artifact_name="../secret.json",
            generated_at="2026-09-30T00:00:00Z",
        )
        self.assertIn("invalid_artifact_name", result["reasons"])
        self.assert_safe(result)

    def test_package_digest_must_be_ready(self):
        package_result = self.package_result()
        package_result["status"] = "hold_public_repair_audit_package"
        result = build_audit_distribution_metadata(
            package_result=package_result,
            artifact_name="public-repair-audit-a" + "a" * 40 + ".json",
            generated_at="2026-09-30T00:00:00Z",
        )
        self.assertIn("package_not_ready", result["reasons"])
        self.assert_safe(result)

    def test_matching_metadata_verifies_against_package(self):
        kwargs = {
            "package_result": self.package_result(),
            "artifact_name": "public-repair-audit-a" + "a" * 40 + ".json",
            "generated_at": "2026-09-30T00:00:00Z",
        }
        built = build_audit_distribution_metadata(**kwargs)
        result = verify_audit_distribution_metadata(
            built["metadata"], self.package_result()
        )
        self.assertEqual(result["status"], "audit_distribution_metadata_verified")
        self.assertIs(result["integrity_verified"], True)
        self.assert_safe(result)

    def test_target_sha_tampering_is_rejected(self):
        kwargs = {
            "package_result": self.package_result(),
            "artifact_name": "public-repair-audit-a" + "a" * 40 + ".json",
            "generated_at": "2026-09-30T00:00:00Z",
        }
        built = build_audit_distribution_metadata(**kwargs)
        tampered = dict(built["metadata"], target_sha="b" * 40)
        result = verify_audit_distribution_metadata(tampered, self.package_result())
        self.assertIn("target_sha_mismatch", result["reasons"])
        self.assert_safe(result)

    def test_package_digest_tampering_is_rejected(self):
        kwargs = {
            "package_result": self.package_result(),
            "artifact_name": "public-repair-audit-a" + "a" * 40 + ".json",
            "generated_at": "2026-09-30T00:00:00Z",
        }
        built = build_audit_distribution_metadata(**kwargs)
        tampered = dict(built["metadata"], package_digest="e" * 64)
        result = verify_audit_distribution_metadata(tampered, self.package_result())
        self.assertIn("package_digest_mismatch", result["reasons"])
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
