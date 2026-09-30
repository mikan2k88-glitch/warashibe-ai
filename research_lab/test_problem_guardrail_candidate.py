"""Regression tests for offline problem-to-guardrail candidate synthesis."""
import unittest

from research_lab.problem_guardrail_candidate import propose_guardrail_candidate


class TestProblemGuardrailCandidate(unittest.TestCase):
    def setUp(self):
        self.problem = {
            "problem_id": "issue-openai-block-001",
            "problem_class": "safety_block",
            "trigger": "scheduled task attempts GitHub Issue comment",
            "blocked_or_failed_action": "write research log to GitHub Issue",
            "safe_expected_behavior": (
                "do not retry or bypass; keep read-only research running and "
                "record the result in the task report or Library when permitted"
            ),
            "evidence_ref": "chat-alert:openai-safety-block",
        }

    def assert_safe(self, result):
        self.assertIs(result["external_action_authorized"], False)
        self.assertIs(result["auto_apply"], False)

    def test_safety_block_becomes_reviewable_candidate(self):
        result = propose_guardrail_candidate(self.problem)
        self.assertEqual(result["status"], "guardrail_candidate_reviewable")
        self.assertIs(result["reviewable"], True)
        self.assertEqual(result["candidate"]["scope"], "research-lab")
        self.assertEqual(result["candidate"]["problem_class"], "safety_block")
        self.assertIn("do not retry or bypass", result["candidate"]["instead"])
        self.assert_safe(result)

    def test_candidate_does_not_authorize_or_auto_apply(self):
        result = propose_guardrail_candidate(self.problem)
        self.assert_safe(result)

    def test_missing_fields_hold(self):
        for field in (
            "problem_id",
            "problem_class",
            "trigger",
            "blocked_or_failed_action",
            "safe_expected_behavior",
            "evidence_ref",
        ):
            with self.subTest(field=field):
                problem = dict(self.problem)
                problem[field] = ""
                result = propose_guardrail_candidate(problem)
                self.assertEqual(result["status"], "hold_guardrail_candidate")
                self.assertIs(result["reviewable"], False)
                self.assertIsNone(result["candidate"])
                self.assertIn("missing_required_field", result["reasons"])
                self.assert_safe(result)

    def test_unknown_problem_class_holds(self):
        problem = dict(self.problem, problem_class="mystery")
        result = propose_guardrail_candidate(problem)
        self.assertIn("unknown_problem_class", result["reasons"])
        self.assertIsNone(result["candidate"])
        self.assert_safe(result)

    def test_resolved_problem_holds(self):
        problem = dict(self.problem, resolved=True)
        result = propose_guardrail_candidate(problem)
        self.assertIn("problem_already_resolved", result["reasons"])
        self.assert_safe(result)

    def test_permission_expansion_holds(self):
        problem = dict(self.problem, requires_permission_expansion=True)
        result = propose_guardrail_candidate(problem)
        self.assertIn("permission_expansion_not_allowed", result["reasons"])
        self.assert_safe(result)

    def test_live_commerce_holds(self):
        problem = dict(self.problem, touches_live_commerce=True)
        result = propose_guardrail_candidate(problem)
        self.assertIn("live_commerce_out_of_scope", result["reasons"])
        self.assert_safe(result)

    def test_non_mapping_holds(self):
        result = propose_guardrail_candidate(None)
        self.assertIn("invalid_problem_record", result["reasons"])
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
