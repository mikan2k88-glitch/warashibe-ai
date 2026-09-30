"""Regression tests for the canonical audit distribution bundle."""
import unittest

from research_lab.problem_repair_audit_distribution_bundle import (
    build_audit_distribution_bundle,
    verify_audit_distribution_bundle,
)


class TestProblemRepairAuditDistributionBundle(unittest.TestCase):
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

    def assert_safe(self, result):
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)

    def test_build_and_verify_bundle(self):
        built = build_audit_distribution_bundle(
            self.package_result(), self.metadata_result()
        )
        self.assertEqual(built["status"], "audit_distribution_bundle_ready")
        self.assertIs(built["integrity_ready"], True)
        self.assertEqual(len(built["bundle"]["bundle_digest"]), 64)
        verified = verify_audit_distribution_bundle(
            built["bundle"], self.package_result(), self.metadata_result()
        )
        self.assertEqual(verified["status"], "audit_distribution_bundle_verified")
        self.assertIs(verified["integrity_verified"], True)
        self.assert_safe(verified)

    def test_key_order_does_not_change_digest(self):
        built = build_audit_distribution_bundle(self.package_result(), self.metadata_result())
        bundle = built["bundle"]
        reordered = {key: bundle[key] for key in reversed(tuple(bundle))}
        verified = verify_audit_distribution_bundle(reordered)
        self.assertEqual(verified["status"], "audit_distribution_bundle_verified")

    def test_bundle_digest_detects_tampering(self):
        built = build_audit_distribution_bundle(self.package_result(), self.metadata_result())
        tampered = dict(built["bundle"])
        tampered["package"] = dict(
            tampered["package"],
            summary={"verification_status": "tampered"},
        )
        result = verify_audit_distribution_bundle(tampered)
        self.assertEqual(result["status"], "audit_distribution_bundle_mismatch")
        self.assertIn("bundle_digest_mismatch", result["reasons"])
        self.assert_safe(result)

    def test_embedded_package_digest_mismatch_is_rejected(self):
        built = build_audit_distribution_bundle(self.package_result(), self.metadata_result())
        tampered = dict(built["bundle"])
        tampered["package_digest"] = "d" * 64
        result = verify_audit_distribution_bundle(tampered)
        self.assertIn("embedded_package_digest_mismatch", result["reasons"])
        self.assert_safe(result)

    def test_embedded_metadata_mismatch_is_rejected(self):
        built = build_audit_distribution_bundle(self.package_result(), self.metadata_result())
        tampered = dict(built["bundle"])
        tampered["metadata"] = dict(tampered["metadata"], artifact_id="d" * 64)
        result = verify_audit_distribution_bundle(tampered)
        self.assertIn("embedded_artifact_id_mismatch", result["reasons"])
        self.assert_safe(result)

    def test_unknown_field_is_rejected(self):
        built = build_audit_distribution_bundle(self.package_result(), self.metadata_result())
        tampered = dict(built["bundle"], unexpected="blocked")
        result = verify_audit_distribution_bundle(tampered)
        self.assertIn("unexpected_bundle_field", result["reasons"])
        self.assert_safe(result)

    def test_source_objects_must_match_embedded_objects(self):
        built = build_audit_distribution_bundle(self.package_result(), self.metadata_result())
        changed_package = self.package_result()
        changed_package["package"] = dict(changed_package["package"], target_sha="d" * 40)
        result = verify_audit_distribution_bundle(
            built["bundle"], changed_package, self.metadata_result()
        )
        self.assertIn("source_package_mismatch", result["reasons"])
        self.assert_safe(result)

    def test_invalid_inputs_are_fail_closed(self):
        result = build_audit_distribution_bundle(
            {"status": "hold"}, self.metadata_result()
        )
        self.assertIn("package_not_ready", result["reasons"])
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
