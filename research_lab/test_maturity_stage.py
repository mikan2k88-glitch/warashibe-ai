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


def main():
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(MaturityTests))
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
