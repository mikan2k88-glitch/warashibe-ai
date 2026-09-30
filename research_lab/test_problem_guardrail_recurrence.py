"""Regression tests for offline guardrail recurrence evaluation."""
import unittest

from research_lab.problem_guardrail_candidate import propose_guardrail_candidate
from research_lab.problem_guardrail_recurrence import evaluate_guardrail_recurrence


class TestProblemGuardrailRecurrence(unittest.TestCase):
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
        self.candidate = propose_guardrail_candidate(self.problem)

    def assert_safe(self, result):
        self.assertIs(result["external_action_authorized"], False)
        self.assertIs(result["auto_repair_authorized"], False)

    def event(self, *, outcome="blocked_before_action", **changes):
        event = {
            "problem_class": "safety_block",
            "trigger": "scheduled task attempts GitHub Issue comment",
            "attempted_action": "write research log to GitHub Issue",
            "outcome": outcome,
        }
        event.update(changes)
        return event

    def test_contained_recurrence_marks_guardrail_effective(self):
        result = evaluate_guardrail_recurrence(
            self.candidate, self.event(outcome="blocked_before_action")
        )
        self.assertEqual(result["status"], "recurrence_contained")
        self.assertIs(result["recurrence_detected"], True)
        self.assertIs(result["guardrail_effective"], True)
        self.assert_safe(result)

    def test_attempted_recurrence_marks_not_contained(self):
        result = evaluate_guardrail_recurrence(
            self.candidate, self.event(outcome="attempted")
        )
        self.assertEqual(result["status"], "recurrence_not_contained")
        self.assertIs(result["recurrence_detected"], True)
        self.assertIs(result["guardrail_effective"], False)
        self.assertIn("unsafe_pattern_recurred", result["reasons"])
        self.assert_safe(result)

    def test_completed_recurrence_marks_not_contained(self):
        result = evaluate_guardrail_recurrence(
            self.candidate, self.event(outcome="completed")
        )
        self.assertEqual(result["status"], "recurrence_not_contained")
        self.assertIs(result["guardrail_effective"], False)
        self.assert_safe(result)

    def test_different_problem_is_not_a_recurrence(self):
        result = evaluate_guardrail_recurrence(
            self.candidate, self.event(trigger="different trigger")
        )
        self.assertEqual(result["status"], "no_matching_recurrence")
        self.assertIs(result["recurrence_detected"], False)
        self.assertIsNone(result["guardrail_effective"])
        self.assert_safe(result)

    def test_unknown_outcome_holds(self):
        result = evaluate_guardrail_recurrence(
            self.candidate, self.event(outcome="mystery")
        )
        self.assertEqual(result["status"], "hold_recurrence_check")
        self.assertIn("unknown_event_outcome", result["reasons"])
        self.assert_safe(result)

    def test_unreviewable_candidate_holds(self):
        bad_candidate = dict(self.candidate, status="hold_guardrail_candidate")
        result = evaluate_guardrail_recurrence(bad_candidate, self.event())
        self.assertIn("candidate_not_reviewable", result["reasons"])
        self.assert_safe(result)

    def test_scope_must_remain_research_lab(self):
        bad_candidate = dict(self.candidate)
        bad_candidate["candidate"] = dict(
            self.candidate["candidate"], scope="production"
        )
        result = evaluate_guardrail_recurrence(bad_candidate, self.event())
        self.assertIn("scope_not_allowed", result["reasons"])
        self.assert_safe(result)

    def test_invalid_inputs_hold(self):
        for candidate, event in ((None, self.event()), (self.candidate, None)):
            with self.subTest(candidate=candidate, event=event):
                result = evaluate_guardrail_recurrence(candidate, event)
                self.assertIn("invalid_input", result["reasons"])
                self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
