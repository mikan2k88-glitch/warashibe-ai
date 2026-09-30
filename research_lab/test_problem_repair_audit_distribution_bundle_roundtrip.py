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

    def test_roundtrip_preserves_bundle_and_digest(self):
        original = self.bundle()
        serialized = serialize_audit_distribution_bundle(original)
        received = deserialize_audit_distribution_bundle(serialized)
        self.assertEqual(received, original)
        verified = verify_serialized_audit_distribution_bundle(serialized)
        self.assertEqual(verified["status"], "audit_distribution_bundle_verified")
        self.assertIs(verified["integrity_verified"], True)
        self.assertEqual(verified["observed_bundle_digest"], original["bundle_digest"])
        self.assert_safe(verified)

    def test_key_order_is_canonicalized(self):
        original = self.bundle()
        reordered = {key: original[key] for key in reversed(tuple(original))}
        serialized_original = serialize_audit_distribution_bundle(original)
        serialized_reordered = serialize_audit_distribution_bundle(reordered)
        self.assertEqual(serialized_original, serialized_reordered)

    def test_tampering_after_serialization_is_detected(self):
        original = self.bundle()
        received = deserialize_audit_distribution_bundle(
            serialize_audit_distribution_bundle(original)
        )
        received["artifact_name"] = "public-repair-audit-" + "d" * 40 + ".json"
        result = verify_serialized_audit_distribution_bundle(
            json.dumps(received, sort_keys=True, separators=(",", ":"))
        )
        self.assertEqual(result["status"], "hold_audit_distribution_bundle_integrity")
        self.assertIn("embedded_artifact_name_mismatch", result["reasons"])
        self.assert_safe(result)

    def test_embedded_object_tampering_is_detected(self):
        original = self.bundle()
        received = deserialize_audit_distribution_bundle(
            serialize_audit_distribution_bundle(original)
        )
        received["metadata"] = dict(received["metadata"], artifact_id="d" * 64)
        result = verify_serialized_audit_distribution_bundle(
            json.dumps(received, sort_keys=True, separators=(",", ":"))
        )
        self.assertIn("embedded_artifact_id_mismatch", result["reasons"])
        self.assert_safe(result)

    def test_unknown_field_is_rejected_after_transport(self):
        original = self.bundle()
        received = deserialize_audit_distribution_bundle(
            serialize_audit_distribution_bundle(original)
        )
        received["unexpected"] = "blocked"
        result = verify_serialized_audit_distribution_bundle(
            json.dumps(received, sort_keys=True, separators=(",", ":"))
        )
        self.assertIn("unexpected_bundle_field", result["reasons"])
        self.assert_safe(result)

    def test_invalid_json_is_fail_closed(self):
        result = verify_serialized_audit_distribution_bundle("{not-json")
        self.assertIn("invalid_serialized_bundle", result["reasons"])
        self.assert_safe(result)

    def test_non_object_json_is_fail_closed(self):
        result = verify_serialized_audit_distribution_bundle("[]")
        self.assertIn("invalid_serialized_bundle", result["reasons"])
        self.assert_safe(result)

    def test_unverified_bundle_cannot_be_serialized(self):
        with self.assertRaises(ValueError):
            serialize_audit_distribution_bundle({"bundle_schema_version": "1.0"})


if __name__ == "__main__":
    unittest.main()
