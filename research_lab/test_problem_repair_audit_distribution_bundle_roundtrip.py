"""Regression tests for audit distribution bundle JSON round-trips."""
import json
import unittest

from research_lab.problem_repair_audit_distribution_bundle import (
    build_audit_distribution_bundle,
)
from research_lab.problem_repair_audit_distribution_bundle_roundtrip import (
    deserialize_audit_distribution_bundle,
    serialize_audit_distribution_bundle,
    verify_serialized_audit_distribution_bundle,
)


class TestProblemRepairAuditDistributionBundleRoundtrip(unittest.TestCase):
    def package_result(self):
        return {
            "status": "public_repair_audit_package_ready",
            "integrity_ready": True,
            "package": {
                "package_schema_version": "1.0",
                "package_type": "warashibe-ai-public-repair-audit",
                "target_sha": "a" * 40,
                "package_digest_algorithm": "sha256",
                "package_digest": "b" * 64,
                "summary": {"verification_status": "verified"},
            },
        }

    def metadata_result(self):
        return {
            "status": "audit_distribution_metadata_ready",
            "integrity_ready": True,
            "metadata": {
                "metadata_schema_version": "1.0",
                "metadata_type": "warashibe-ai-public-repair-audit-distribution",
                "artifact_name": "public-repair-audit-" + "a" * 40 + ".json",
                "generated_at": "2026-09-30T15:00:00Z",
                "target_sha": "a" * 40,
                "package_schema_version": "1.0",
                "package_digest_algorithm": "sha256",
                "package_digest": "b" * 64,
                "artifact_id": "c" * 64,
            },
        }

    def bundle(self):
        result = build_audit_distribution_bundle(
            self.package_result(), self.metadata_result()
        )
        self.assertEqual(result["status"], "audit_distribution_bundle_ready")
        return result["bundle"]

    def assert_safe(self, result):
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)

    def test_roundtrip_preserves_verified_bundle(self):
        bundle = self.bundle()
        serialized = serialize_audit_distribution_bundle(bundle)
        restored = deserialize_audit_distribution_bundle(serialized)
        self.assertEqual(restored, bundle)

        verified = verify_serialized_audit_distribution_bundle(serialized)
        self.assertEqual(verified["status"], "audit_distribution_bundle_verified")
        self.assertIs(verified["integrity_verified"], True)
        self.assertEqual(verified["observed_bundle_digest"], bundle["bundle_digest"])
        self.assert_safe(verified)

    def test_serialization_is_deterministic(self):
        bundle = self.bundle()
        first = serialize_audit_distribution_bundle(bundle)
        second = serialize_audit_distribution_bundle(dict(reversed(list(bundle.items()))))
        self.assertEqual(first, second)

    def test_tampered_bundle_digest_is_rejected(self):
        bundle = self.bundle()
        tampered = dict(bundle, bundle_digest="d" * 64)
        serialized = json.dumps(tampered, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        result = verify_serialized_audit_distribution_bundle(serialized)
        self.assertEqual(result["status"], "audit_distribution_bundle_mismatch")
        self.assertIn("bundle_digest_mismatch", result["reasons"])
        self.assert_safe(result)

    def test_extra_field_is_rejected(self):
        bundle = self.bundle()
        bundle["extra"] = "blocked"
        serialized = json.dumps(bundle, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        result = verify_serialized_audit_distribution_bundle(serialized)
        self.assertIn("unexpected_bundle_field", result["reasons"])
        self.assert_safe(result)

    def test_non_object_json_is_rejected(self):
        result = verify_serialized_audit_distribution_bundle("[]")
        self.assertIn("invalid_serialized_bundle", result["reasons"])
        self.assert_safe(result)

    def test_invalid_json_is_rejected(self):
        result = verify_serialized_audit_distribution_bundle("{bad json")
        self.assertIn("invalid_serialized_bundle", result["reasons"])
        self.assert_safe(result)

    def test_unverified_bundle_cannot_be_serialized(self):
        with self.assertRaises(ValueError):
            serialize_audit_distribution_bundle({"bundle_schema_version": "1.0"})


if __name__ == "__main__":
    unittest.main()
