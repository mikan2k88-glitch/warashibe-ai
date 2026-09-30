"""TDD contract for the AI-side state transition after consumer verification."""

import unittest

from research_lab.autonomous_research_consumer_state_transition import (
    decide_consumer_state_transition,
)


class TestAutonomousResearchConsumerStateTransition(unittest.TestCase):
    def test_accept_advances_to_next_theme(self):
        result = decide_consumer_state_transition(
            {"decision": "accept", "integrity_verified": True}
        )
        self.assertEqual(result["status"], "consumer_state_transition_ready")
        self.assertEqual(result["next_state"], "advance_to_next_theme")
        self.assertEqual(result["action"] , "continue_research")
        self.assertEqual(result["reason_code"], "audit_bundle_verified")
        self.assert_safe(result)

    def test_reject_routes_to_repair(self):
        result = decide_consumer_state_transition(
            {
                "decision": "reject",
                "integrity_verified": False,
                "reason_codes": ("bundle_digest_mismatch",),
            }
        )
        self.assertEqual(result["next_state"], "repair_current_audit")
        self.assertEqual(result["action"], "prepare_repair_candidate")
        self.assertEqual(result["reason_code"], "audit_bundle_rejected")
        self.assert_safe(result)

    def test_hold_waits_for_more_evidence(self):
        result = decide_consumer_state_transition(
            {
                "decision": "hold",
                "integrity_verified": False,
                "reason_codes": ("invalid_bundle",),
            }
        )
        self.assertEqual(result["next_state"], "await_more_evidence")
        self.assertEqual(result["action"], "schedule_recheck")
        self.assertEqual(result["reason_code"], "audit_bundle_on_hold")
        self.assert_safe(result)

    def test_unknown_decision_fails_closed(self):
        result = decide_consumer_state_transition(
            {"decision": "unknown", "integrity_verified": True}
        )
        self.assertEqual(result["next_state"], "await_more_evidence")
        self.assertEqual(result["action"], "schedule_recheck")
        self.assertEqual(result["reason_code"], "unknown_consumer_decision")
        self.assert_safe(result)

    def test_accept_without_integrity_is_not_allowed(self):
        result = decide_consumer_state_transition(
            {"decision": "accept", "integrity_verified": False}
        )
        self.assertEqual(result["next_state"], "await_more_evidence")
        self.assertEqual(result["reason_code"], "accept_without_integrity")
        self.assert_safe(result)

    def test_missing_result_fails_closed(self):
        result = decide_consumer_state_transition(None)
        self.assertEqual(result["next_state"], "await_more_evidence")
        self.assertEqual(result["reason_code"], "invalid_consumer_result")
        self.assert_safe(result)

    def assert_safe(self, result):
        self.assertIs(result["external_runtime_action_authorized"], False)
        self.assertIs(result["auto_retry_authorized"], False)
        self.assertIs(result["auto_rollback_authorized"], False)
        self.assertIs(result["human_gate_required"], False)
        self.assertIs(result["read_only"], True)


if __name__ == "__main__":
    unittest.main()
