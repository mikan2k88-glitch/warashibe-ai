"""PG-037 execution boundary regressions."""
import unittest

from research_lab.maturity_stage import stage_contract, require_operation, transition_stage


class MaturityTests(unittest.TestCase):
    def test_commerce_never_authorized(self):
        for stage in stage_contract("research")["stages"]:
            contract = stage_contract(stage)
            self.assertFalse(contract["external_execution_authorized"])
            self.assertTrue(contract["human_gate_required"])
            for operation in ("real_purchase", "real_payment", "real_listing", "real_sale", "refund"):
                with self.assertRaises(ValueError):
                    require_operation(stage, operation)
        require_operation("shadow", "shadow_observation")

    def test_transitions_fail_closed(self):
        self.assertEqual(transition_stage("research", "offline_validation")["maturity_stage"], "offline_validation")
        for current, target in (("research", "shadow"), ("human_gate", "limited_live"), ("shadow", "bogus")):
            with self.assertRaises(ValueError):
                transition_stage(current, target)
        with self.assertRaises(ValueError):
            require_operation("shadow", "unknown_operation")

    def test_existing_human_decision_is_required_and_expires(self):
        from research_lab.human_go_no_go import build_human_go_no_go_decision
        audit = {"status": "live_readiness_audit_complete", "audit_key": "fixture-audit",
                 "ready_for_human_go_no_go": True, "human_go_no_go_required": True,
                 "live_commerce_authorized": False}
        decision = build_human_go_no_go_decision(
            audit, decision_key="fixture-decision", decision="go", reviewer_id="fixture-human",
            decided_at="2026-10-05T00:00:00Z", valid_until="2026-10-06T00:00:00Z",
            reason="fixture only", approved_budget_jpy=1000, max_transactions=1, approved_providers=["fixture"],
        )
        for clock in ("2026-10-04T00:00:00Z", "2026-10-06T00:00:00Z", None):
            with self.assertRaises(ValueError):
                transition_stage("human_gate", "limited_live", human_decision=decision, readiness_audit=audit, as_of=clock)
        advanced = transition_stage("human_gate", "limited_live", human_decision=decision,
                                    readiness_audit=audit, as_of="2026-10-05T01:00:00Z")
        self.assertFalse(advanced["external_execution_authorized"])
        self.assertFalse(advanced["purchase_authorized"])
        tampered = {**decision, "purchase_authorized": True}
        with self.assertRaises(ValueError):
            transition_stage("human_gate", "limited_live", human_decision=tampered,
                             readiness_audit=audit, as_of="2026-10-05T01:00:00Z")


def main():
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(MaturityTests))
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
