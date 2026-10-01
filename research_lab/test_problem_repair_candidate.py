"""Regression tests for recurring-problem repair candidate synthesis."""
import unittest

from research_lab.problem_guardrail_candidate import propose_guardrail_candidate
from research_lab.problem_guardrail_recurrence import evaluate_guardrail_recurrence
from research_lab.problem_repair_candidate import propose_repair_candidate


class TestProblemRepairCandidate(unittest.TestCase):
    def setUp(self):
        problem = {
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
        candidate = propose_guardrail_candidate(problem)
        self.recurrence = evaluate_guardrail_recurrence(
            candidate,
            {
                "problem_class": "safety_block",
                "trigger": "scheduled task attempts GitHub Issue comment",
                "attempted_action": "write research log to GitHub Issue",
                "outcome": "attempted",
            },
        )

    def assert_safe(self, result):
        self.assertIs(result["external_action_authorized"], False)
        self.assertIs(result["auto_repair_authorized"], False)
        self.assertEqual(result["max_repairs_this_cycle"], 1)

    def test_actionable_recurrence_yields_single_reviewable_candidate(self):
        result = propose_repair_candidate(
            self.recurrence,
            repair_kind="clarify_instruction",
            target="scheduled research task instruction",
            rationale="prevent GitHub Issue writes and keep safe read-only research running",
        )
        self.assertEqual(result["status"], "repair_candidate_reviewable")
        self.assertIs(result["reviewable"], True)
        self.assertEqual(result["repair_candidate"]["scope"], "research-lab")
        self.assertIs(result["repair_candidate"]["requires_ai_decision"], True)
        self.assertIs(result["repair_candidate"]["human_gate_required"], False)
        self.assertIs(result["repair_candidate"]["single_repair_only"], True)
        self.assert_safe(result)

    def test_non_actionable_recurrence_holds(self):
        recurrence = dict(self.recurrence, status="recurrence_contained", guardrail_effective=True)
        result = propose_repair_candidate(
            recurrence,
            repair_kind="add_test",
            target="research task regression",
            rationale="confirm contained behavior",
        )
        self.assertIn("recurrence_not_actionable", result["reasons"])
        self.assertIsNone(result["repair_candidate"])
        self.assert_safe(result)

    def test_unknown_repair_kind_holds(self):
        result = propose_repair_candidate(
            self.recurrence,
            repair_kind="rewrite_everything",
            target="research task",
            rationale="too broad",
        )
        self.assertIn("repair_kind_not_allowed", result["reasons"])
        self.assert_safe(result)

    def test_forbidden_scope_terms_hold(self):
        cases = (
            ("main branch workflow", "tighten gate"),
            ("research task", "change production behavior"),
            ("research task", "rotate secret"),
            ("research task", "change payment logic"),
            ("research task", "enable live db write"),
            ("research task", "permission expansion"),
        )
        for target, rationale in cases:
            with self.subTest(target=target, rationale=rationale):
                result = propose_repair_candidate(
                    self.recurrence,
                    repair_kind="tighten_gate",
                    target=target,
                    rationale=rationale,
                )
                self.assertIn("repair_scope_not_allowed", result["reasons"])
                self.assert_safe(result)

    def test_empty_description_holds(self):
        result = propose_repair_candidate(
            self.recurrence,
            repair_kind="add_validation",
            target="",
            rationale="missing target",
        )
        self.assertIn("invalid_repair_description", result["reasons"])
        self.assert_safe(result)

    def test_invalid_recurrence_input_holds(self):
        result = propose_repair_candidate(
            None,
            repair_kind="add_test",
            target="research task",
            rationale="test",
        )
        self.assertIn("invalid_recurrence_result", result["reasons"])
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
