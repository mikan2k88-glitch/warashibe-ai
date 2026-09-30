"""Tests for the bounded live hourly scheduler connector."""
import unittest

from research_lab.scheduler_live_connector import decide_scheduler_live_connector


class TestSchedulerLiveConnector(unittest.TestCase):
    def assert_safe(self, result):
        self.assertIs(result["read_only"], True)
        self.assertIs(result["human_gate_required"], False)
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)

    def test_due_slot_is_ready_for_chatgpt_schedule(self):
        result = decide_scheduler_live_connector(
            {"slot": "2026-09-30T16:00Z", "source": "chatgpt_schedule"}
        )
        self.assertEqual(result["status"], "scheduler_connector_ready")
        self.assertEqual(result["next_action"], "run_research_cycle")
        self.assertEqual(result["reason_code"], "hourly_slot_due")
        self.assert_safe(result)

    def test_same_slot_is_not_run_twice(self):
        result = decide_scheduler_live_connector(
            {
                "slot": "2026-09-30T17:00Z",
                "source": "chatgpt_schedule",
                "last_completed_slot": "2026-09-30T17:00Z",
            }
        )
        self.assertEqual(result["status"], "scheduler_connector_skip")
        self.assertEqual(result["next_action"], "no_op")
        self.assertEqual(result["reason_code"], "hourly_slot_already_completed")
        self.assert_safe(result)

    def test_in_progress_ci_blocks_duplicate_execution(self):
        result = decide_scheduler_live_connector(
            {
                "slot": "2026-09-30T18:00Z",
                "source": "chatgpt_schedule",
                "ci_state": "in_progress",
            }
        )
        self.assertEqual(result["status"], "scheduler_connector_hold")
        self.assertEqual(result["reason_code"], "ci_already_in_progress")
        self.assert_safe(result)

    def test_success_with_matching_sha_is_not_repeated(self):
        result = decide_scheduler_live_connector(
            {
                "slot": "2026-09-30T19:00Z",
                "source": "chatgpt_schedule",
                "ci_state": "success",
                "current_head_sha": "abc123",
                "ci_head_sha": "abc123",
            }
        )
        self.assertEqual(result["status"], "scheduler_connector_skip")
        self.assertEqual(result["reason_code"], "same_head_already_verified")
        self.assert_safe(result)

    def test_success_with_sha_mismatch_holds(self):
        result = decide_scheduler_live_connector(
            {
                "slot": "2026-09-30T20:00Z",
                "source": "chatgpt_schedule",
                "ci_state": "success",
                "current_head_sha": "abc123",
                "ci_head_sha": "def456",
            }
        )
        self.assertEqual(result["status"], "scheduler_connector_hold")
        self.assertEqual(result["reason_code"], "ci_sha_mismatch")
        self.assert_safe(result)

    def test_failed_ci_does_not_auto_retry(self):
        result = decide_scheduler_live_connector(
            {
                "slot": "2026-09-30T21:00Z",
                "source": "chatgpt_schedule",
                "ci_state": "failure",
            }
        )
        self.assertEqual(result["status"], "scheduler_connector_hold")
        self.assertEqual(result["reason_code"], "ci_failure_requires_research_review")
        self.assert_safe(result)

    def test_unknown_source_holds(self):
        result = decide_scheduler_live_connector(
            {"slot": "2026-09-30T22:00Z", "source": "unknown"}
        )
        self.assertEqual(result["status"], "scheduler_connector_hold")
        self.assertEqual(result["reason_code"], "unknown_scheduler_source")
        self.assert_safe(result)

    def test_invalid_slot_holds(self):
        result = decide_scheduler_live_connector(
            {"slot": "not-a-slot", "source": "chatgpt_schedule"}
        )
        self.assertEqual(result["status"], "scheduler_connector_hold")
        self.assertEqual(result["reason_code"], "invalid_hourly_slot")
        self.assert_safe(result)

    def test_missing_input_holds(self):
        result = decide_scheduler_live_connector(None)
        self.assertEqual(result["status"], "scheduler_connector_hold")
        self.assertEqual(result["reason_code"], "invalid_connector_input")
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
