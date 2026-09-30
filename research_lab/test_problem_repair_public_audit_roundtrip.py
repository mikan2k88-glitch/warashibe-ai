"""Regression tests for serialized public repair audit package round-trips."""
import unittest

from research_lab.problem_repair_public_audit_package import (
    build_public_repair_audit_package,
)
from research_lab.problem_repair_public_audit_roundtrip import (
    deserialize_public_repair_audit_package,
    serialize_public_repair_audit_package,
    verify_serialized_public_repair_audit_package,
)


class TestProblemRepairPublicAuditRoundtrip(unittest.TestCase):
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

    def package(self):
        result = build_public_repair_audit_package(self.summary_result())
        self.assertEqual(result["status"], "public_repair_audit_package_ready")
        return result["package"]

    def assert_safe(self, result):
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)

    def test_roundtrip_preserves_verified_package(self):
        package = self.package()
        serialized = serialize_public_repair_audit_package(package)
        restored = deserialize_public_repair_audit_package(serialized)
        self.assertEqual(restored, package)

        verified = verify_serialized_public_repair_audit_package(serialized)
        self.assertEqual(
            verified["status"], "public_repair_audit_package_verified"
        )
        self.assertIs(verified["integrity_verified"], True)
        self.assert_safe(verified)

    def test_serialization_is_deterministic(self):
        package = self.package()
        first = serialize_public_repair_audit_package(package)
        second = serialize_public_repair_audit_package(dict(reversed(list(package.items()))))
        self.assertEqual(first, second)

    def test_non_object_json_is_rejected(self):
        result = deserialize_public_repair_audit_package("[]")
        self.assertIn("invalid_serialized_package", result["reasons"])
        self.assert_safe(result)

    def test_invalid_json_is_rejected(self):
        result = deserialize_public_repair_audit_package("{bad json")
        self.assertIn("invalid_serialized_package", result["reasons"])
        self.assert_safe(result)

    def test_extra_field_is_rejected(self):
        package = self.package()
        package["extra"] = "tampered"
        serialized = serialize_public_repair_audit_package(package, allow_unvalidated=True)
        result = verify_serialized_public_repair_audit_package(serialized)
        self.assertIn("unexpected_package_field", result["reasons"])
        self.assert_safe(result)

    def test_tampered_serialized_summary_is_rejected(self):
        package = self.package()
        serialized = serialize_public_repair_audit_package(package)
        tampered = serialized.replace("sha-final", "sha-tampered")
        result = verify_serialized_public_repair_audit_package(tampered)
        self.assertIn("target_sha_mismatch", result["reasons"])
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
