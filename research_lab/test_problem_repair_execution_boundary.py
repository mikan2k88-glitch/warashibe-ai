"""Regression tests for bounded AI repair execution plans."""
import unittest

from research_lab.problem_repair_execution_boundary import build_repair_execution_plan


class TestProblemRepairExecutionBoundary(unittest.TestCase):
    def setUp(self):
        self.ai_decision = {
            "status": "ai_repair_authorized",
            "decision_authority": "ai",
            "human_gate_required": False,
            "code_repair_authorized": True,
            "external_runtime_action_authorized": False,
            "max_repairs_this_cycle": 1,
            "reasons": (),
        }

    def assert_safe(self, result):
        self.assertEqual(result["decision_authority"], "ai")
        self.assertIs(result["human_gate_required"], False)
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertEqual(result["max_files_changed"], 1)
        self.assertEqual(result["max_repairs_this_cycle"], 1)

    def test_single_research_lab_python_change_is_authorized(self):
        result = build_repair_execution_plan(
            self.ai_decision,
            path="research_lab/sample_guard.py",
            change_summary="tighten fail-closed validation for malformed input",
            expected_test="python -m research_lab.test_sample_guard",
        )
        self.assertEqual(result["status"], "repair_execution_plan_ready")
        self.assertIs(result["git_write_authorized"], True)
        self.assertEqual(result["plan"]["branch"], "research-lab")
        self.assertIs(result["plan"]["single_file_only"], True)
        self.assertIs(result["plan"]["requires_same_sha_ci_after_write"], True)
        self.assertIs(result["plan"]["stop_on_ci_failure_or_unknown"], True)
        self.assert_safe(result)

    def test_ai_authorization_is_required(self):
        decision = dict(self.ai_decision, status="hold_ai_repair")
        result = build_repair_execution_plan(
            decision,
            path="research_lab/sample_guard.py",
            change_summary="tighten validation",
            expected_test="python -m research_lab.test_sample_guard",
        )
        self.assertIn("ai_repair_not_authorized", result["reasons"])
        self.assertIs(result["git_write_authorized"], False)
        self.assert_safe(result)

    def test_only_research_lab_python_paths_are_allowed(self):
        for path in (
            "app.py",
            ".github/workflows/research-lab.yml",
            "docs/PROJECT_SPEC.md",
            "../research_lab/escape.py",
            "/research_lab/absolute.py",
        ):
            with self.subTest(path=path):
                result = build_repair_execution_plan(
                    self.ai_decision,
                    path=path,
                    change_summary="tighten validation",
                    expected_test="python -m research_lab.test_sample_guard",
                )
                self.assertIs(result["git_write_authorized"], False)
                self.assertTrue(
                    "path_not_allowed" in result["reasons"]
                    or "file_type_not_allowed" in result["reasons"]
                )
                self.assert_safe(result)

    def test_forbidden_scope_terms_hold(self):
        for text in (
            "modify main behavior",
            "change production config",
            "rotate secret",
            "update credential handling",
            "change payment flow",
            "enable live db write",
            "permission expansion",
            "invoke external ai",
            "force push branch",
        ):
            with self.subTest(text=text):
                result = build_repair_execution_plan(
                    self.ai_decision,
                    path="research_lab/sample_guard.py",
                    change_summary=text,
                    expected_test="python -m research_lab.test_sample_guard",
                )
                self.assertIn("execution_scope_not_allowed", result["reasons"])
                self.assertIs(result["git_write_authorized"], False)
                self.assert_safe(result)

    def test_invalid_plan_fields_hold(self):
        result = build_repair_execution_plan(
            self.ai_decision,
            path="research_lab/sample_guard.py",
            change_summary="",
            expected_test="python -m research_lab.test_sample_guard",
        )
        self.assertIn("invalid_execution_plan", result["reasons"])
        self.assertIs(result["git_write_authorized"], False)
        self.assert_safe(result)

    def test_invalid_ai_decision_holds(self):
        result = build_repair_execution_plan(
            None,
            path="research_lab/sample_guard.py",
            change_summary="tighten validation",
            expected_test="python -m research_lab.test_sample_guard",
        )
        self.assertIn("invalid_ai_decision", result["reasons"])
        self.assertIs(result["git_write_authorized"], False)
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
