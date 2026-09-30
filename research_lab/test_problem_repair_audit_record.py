"""Regression tests for reproducible AI repair audit records."""
import unittest

from research_lab.problem_repair_audit_record import build_repair_audit_record


class TestProblemRepairAuditRecord(unittest.TestCase):
    def setUp(self):
        self.validation_success = {
            "status": "repair_validated_success",
            "repair_success": True,
            "rollback_candidate": False,
        }
        self.validation_failure = {
            "status": "repair_validated_failure",
            "repair_success": False,
            "rollback_candidate": True,
        }

    def assert_safe(self, result):
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)

    def test_successful_repair_is_bound_into_reproducible_record(self):
        result = build_repair_audit_record(
            repair_id="repair-001",
            before_sha="before123",
            after_sha="after456",
            path="research_lab/example.py",
            expected_test="python -m research_lab.test_example",
            validation_result=self.validation_success,
        )
        self.assertEqual(result["status"], "repair_audit_record_ready")
        self.assertIs(result["reproducible"], True)
        record = result["audit_record"]
        self.assertEqual(record["before_sha"], "before123")
        self.assertEqual(record["after_sha"], "after456")
        self.assertEqual(record["path"], "research_lab/example.py")
        self.assertEqual(record["validation_status"], "repair_validated_success")
        self.assertIs(record["repair_success"], True)
        self.assertIs(record["single_file_only"], True)
        self.assert_safe(result)

    def test_failed_repair_is_recorded_without_auto_rollback(self):
        result = build_repair_audit_record(
            repair_id="repair-002",
            before_sha="before123",
            after_sha="after456",
            path="research_lab/example.py",
            expected_test="python -m research_lab.test_example",
            validation_result=self.validation_failure,
        )
        self.assertEqual(result["status"], "repair_audit_record_ready")
        self.assertIs(result["audit_record"]["repair_success"], False)
        self.assertIs(result["audit_record"]["rollback_candidate"], True)
        self.assert_safe(result)

    def test_same_sha_is_rejected(self):
        result = build_repair_audit_record(
            repair_id="repair-003",
            before_sha="same",
            after_sha="same",
            path="research_lab/example.py",
            expected_test="python -m research_lab.test_example",
            validation_result=self.validation_success,
        )
        self.assertIn("sha_not_changed", result["reasons"])
        self.assertIs(result["reproducible"], False)
        self.assert_safe(result)

    def test_non_terminal_validation_is_rejected(self):
        result = build_repair_audit_record(
            repair_id="repair-004",
            before_sha="before123",
            after_sha="after456",
            path="research_lab/example.py",
            expected_test="python -m research_lab.test_example",
            validation_result={"status": "repair_validation_hold"},
        )
        self.assertIn("validation_not_terminal", result["reasons"])
        self.assertIsNone(result["audit_record"])
        self.assert_safe(result)

    def test_non_research_lab_python_path_is_rejected(self):
        for path in ("app.py", "../research_lab/x.py", "research_lab/readme.md"):
            with self.subTest(path=path):
                result = build_repair_audit_record(
                    repair_id="repair-005",
                    before_sha="before123",
                    after_sha="after456",
                    path=path,
                    expected_test="python -m research_lab.test_example",
                    validation_result=self.validation_success,
                )
                self.assertIn("path_not_allowed", result["reasons"])
                self.assert_safe(result)

    def test_invalid_input_is_rejected(self):
        result = build_repair_audit_record(
            repair_id="",
            before_sha="before123",
            after_sha="after456",
            path="research_lab/example.py",
            expected_test="python -m research_lab.test_example",
            validation_result=self.validation_success,
        )
        self.assertIn("invalid_audit_input", result["reasons"])
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
