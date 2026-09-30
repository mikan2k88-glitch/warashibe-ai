"""Regression tests for AI-only bounded code repair decisions."""
import unittest

from research_lab.problem_guardrail_candidate import propose_guardrail_candidate
from research_lab.problem_guardrail_recurrence import evaluate_guardrail_recurrence
from research_lab.problem_repair_candidate import propose_repair_candidate
from research_lab.problem_repair_ai_decision import decide_ai_code_repair


class TestProblemRepairAIDecision(unittest.TestCase):
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
        guardrail = propose_guardrail_candidate(problem)
        recurrence = evaluate_guardrail_recurrence(
            guardrail,
            {
                "problem_class": "safety_block",
                "trigger": "scheduled task attempts GitHub Issue comment",
                "attempted_action": "write research log to GitHub Issue",
                "outcome": "attempted",
            },
        )
        self.repair = propose_repair_candidate(
            recurrence,
            repair_kind="clarify_instruction",
            target="scheduled research task instruction",
            rationale="prevent repeated GitHub Issue writes while safe research continues",
        )

    def assert_common(self, result):
        self.assertEqual(result["decision_authority"], "ai")
        self.assertIs(result["human_gate_required"], False)
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertEqual(result["max_repairs_this_cycle"], 1)

    def test_low_risk_research_lab_repair_is_ai_authorized(self):
        result = decide_ai_code_repair(self.repair)
        self.assertEqual(result["status"], "ai_repair_authorized")
        self.assertIs(result["code_repair_authorized"], True)
        self.assertEqual(result["reasons"], ())
        self.assert_common(result)

    def test_unreviewable_candidate_holds(self):
        result = decide_ai_code_repair(
            dict(self.repair, status="hold_repair_candidate")
        )
        self.assertEqual(result["status"], "hold_ai_repair")
        self.assertIs(result["code_repair_authorized"], False)
        self.assertIn("repair_candidate_not_reviewable", result["reasons"])
        self.assert_common(result)

    def test_non_research_scope_holds(self):
        repair = dict(self.repair)
        repair["repair_candidate"] = dict(
            self.repair["repair_candidate"], scope="production"
        )
        result = decide_ai_code_repair(repair)
        self.assertIn("scope_not_allowed", result["reasons"])
        self.assertIs(result["code_repair_authorized"], False)
        self.assert_common(result)

    def test_single_repair_limit_is_required(self):
        repair = dict(self.repair)
        repair["repair_candidate"] = dict(
            self.repair["repair_candidate"], single_repair_only=False
        )
        result = decide_ai_code_repair(repair)
        self.assertIn("single_repair_limit_missing", result["reasons"])
        self.assert_common(result)

    def test_forbidden_targets_hold(self):
        for target in (
            "main workflow",
            "production service",
            "secret rotation",
            "credential handling",
            "payment flow",
            "live db migration",
            "permission expansion",
            "external ai execution",
        ):
            with self.subTest(target=target):
                repair = dict(self.repair)
                repair["repair_candidate"] = dict(
                    self.repair["repair_candidate"],
                    target=target,
                )
                result = decide_ai_code_repair(repair)
                self.assertIn("repair_scope_not_allowed", result["reasons"])
                self.assertIs(result["code_repair_authorized"], False)
                self.assert_common(result)

    def test_invalid_input_holds(self):
        result = decide_ai_code_repair(None)
        self.assertIn("invalid_repair_result", result["reasons"])
        self.assertIs(result["code_repair_authorized"], False)
        self.assert_common(result)


if __name__ == "__main__":
    unittest.main()
