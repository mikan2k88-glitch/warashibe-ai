"""Tests for the bounded hourly research scheduler contract."""
import unittest

from research_lab.hourly_research_scheduler_contract import decide_hourly_research_schedule


class TestHourlyResearchSchedulerContract(unittest.TestCase):
    def assert_safe(self, result):
        self.assertIs(result["read_only"], True)
        self.assertIs(result["human_gate_required"], False)
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)

    def test_accept_advances_to_current_hour_slot(self):
        result = decide_hourly_research_schedule(
            {"decision": "advance_to_next_theme", "slot": "2026-09-30T16:00Z"}
        )
        self.assertEqual(result["status"], "hourly_schedule_ready")
        self.assertEqual(result["next_action"], "run_research_cycle")
        self.assertEqual(result["slot"], "2026-09-30T16:00Z")
        self.assertEqual(result["reason_code"], "hourly_slot_due")
        self.assert_safe(result)

    def test_hold_schedules_recheck_without_repair_execution(self):
        result = decide_hourly_research_schedule(
            {"decision": "hold", "slot": "2026-09-30T17:00Z"}
        )
        self.assertEqual(result["status"], "hourly_schedule_hold")
        self.assertEqual(result["next_action"], "schedule_recheck")
        self.assertEqual(result["reason_code"], "consumer_state_hold")
        self.assert_safe(result)

    def test_reject_does_not_skip_repair_state(self):
        result = decide_hourly_research_schedule(
            {"decision": "repair_current_audit", "slot": "2026-09-30T18:00Z"}
        )
        self.assertEqual(result["status"], "hourly_schedule_ready")
        self.assertEqual(result["next_action"], "prepare_repair_candidate")
        self.assertEqual(result["reason_code"], "repair_state_due")
        self.assert_safe(result)

    def test_duplicate_slot_is_skipped(self):
        result = decide_hourly_research_schedule(
            {
                "decision": "advance_to_next_theme",
                "slot": "2026-09-30T19:00Z",
                "last_completed_slot": "2026-09-30T19:00Z",
            }
        )
        self.assertEqual(result["status"], "hourly_schedule_skip")
        self.assertEqual(result["next_action"], "no_op")
        self.assertEqual(result["reason_code"], "hourly_slot_already_completed")
        self.assert_safe(result)

    def test_invalid_slot_holds(self):
        result = decide_hourly_research_schedule(
            {"decision": "advance_to_next_theme", "slot": "not-a-slot"}
        )
        self.assertEqual(result["status"], "hourly_schedule_hold")
        self.assertEqual(result["next_action"], "schedule_recheck")
        self.assertEqual(result["reason_code"], "invalid_hourly_slot")
        self.assert_safe(result)

    def test_unknown_decision_holds(self):
        result = decide_hourly_research_schedule(
            {"decision": "unknown", "slot": "2026-09-30T20:00Z"}
        )
        self.assertEqual(result["status"], "hourly_schedule_hold")
        self.assertEqual(result["reason_code"], "unknown_consumer_state")
        self.assert_safe(result)

    def test_missing_input_holds(self):
        result = decide_hourly_research_schedule(None)
        self.assertEqual(result["status"], "hourly_schedule_hold")
        self.assertEqual(result["reason_code"], "invalid_schedule_input")
        self.assert_safe(result)


if __name__ == "__main__":
    unittest.main()
