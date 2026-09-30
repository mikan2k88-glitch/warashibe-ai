"""Regression tests for exact-SHA AI repair validation."""
import unittest

from research_lab.problem_repair_validation_gate import evaluate_repair_validation


class TestProblemRepairValidationGate(unittest.TestCase):
    SHA = "abc123"

    def assert_common(self, result):
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)
        self.assertIs(result["external_runtime_action_authorized"], False)

    def test_matching_successful_ci_validates_repair(self):
        result = evaluate_repair_validation(
            expected_sha=self.SHA,
            observed_sha=self.SHA,
            ci_status="completed",
            ci_conclusion="success",
        )
        self.assertEqual(result["status"], "repair_validated_success")
        self.assertIs(result["repair_success"], True)
        self.assertIs(result["rollback_candidate"], False)
        self.assertIs(result["stop_required"], False)
        self.assert_common(result)

    def test_sha_mismatch_holds_fail_closed(self):
        result = evaluate_repair_validation(
            expected_sha=self.SHA,
            observed_sha="different",
            ci_status="completed",
            ci_conclusion="success",
        )
        self.assertEqual(result["status"], "repair_validation_hold")
        self.assertIn("sha_mismatch", result["reasons"])
        self.assertIs(result["stop_required"], True)
        self.assert_common(result)

    def test_incomplete_ci_holds_fail_closed(self):
        result = evaluate_repair_validation(
            expected_sha=self.SHA,
            observed_sha=self.SHA,
            ci_status="in_progress",
            ci_conclusion=None,
        )
        self.assertIn("ci_not_completed", result["reasons"])
        self.assertIs(result["stop_required"], True)
        self.assert_common(result)

    def test_failed_ci_marks_rollback_candidate_without_auto_rollback(self):
        result = evaluate_repair_validation(
            expected_sha=self.SHA,
            observed_sha=self.SHA,
            ci_status="completed",
            ci_conclusion="failure",
        )
        self.assertEqual(result["status"], "repair_validated_failure")
        self.assertIs(result["repair_success"], False)
        self.assertIs(result["rollback_candidate"], True)
        self.assertIs(result["stop_required"], True)
        self.assert_common(result)

    def test_other_terminal_failures_stop(self):
        for conclusion in ("cancelled", "timed_out", "action_required"):
            with self.subTest(conclusion=conclusion):
                result = evaluate_repair_validation(
                    expected_sha=self.SHA,
                    observed_sha=self.SHA,
                    ci_status="completed",
                    ci_conclusion=conclusion,
                )
                self.assertEqual(result["status"], "repair_validated_failure")
                self.assertIs(result["rollback_candidate"], True)
                self.assert_common(result)

    def test_unknown_conclusion_holds(self):
        result = evaluate_repair_validation(
            expected_sha=self.SHA,
            observed_sha=self.SHA,
            ci_status="completed",
            ci_conclusion="neutral",
        )
        self.assertIn("ci_conclusion_unknown", result["reasons"])
        self.assertIs(result["stop_required"], True)
        self.assert_common(result)

    def test_invalid_input_holds(self):
        result = evaluate_repair_validation(
            expected_sha="",
            observed_sha=self.SHA,
            ci_status="completed",
            ci_conclusion="success",
        )
        self.assertIn("invalid_validation_input", result["reasons"])
        self.assert_common(result)


if __name__ == "__main__":
    unittest.main()
