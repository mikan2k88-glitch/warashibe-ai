"""Offline PG-038/039 targeted contracts; all prices are synthetic fixtures."""
from copy import deepcopy
import unittest

from candidate_engine import create_candidate
from research_lab.shadow_validation import create_shadow_candidate, add_shadow_observation, complete_shadow
from research_lab.shadow_repository import InMemoryShadowRepository
from research_lab.promotion_gate import evaluate_promotion

NOW = "2026-10-05T00:00:00+00:00"
LATER = "2026-10-06T00:00:00+00:00"
IDENTITY = {"product_id": "fixture-001", "edition": "standard", "model": "fixture",
            "jan": "fixture-jan", "condition": "used_good", "included_items": ["case", "manual"]}


def fixture():
    candidate = create_candidate("Fixture only", 1000, 2000, "fixture", category="game",
                                 liquidity_score=0.8, estimated_days_to_sell=5,
                                 authenticity_status="verified", return_risk="low")
    amounts = {"acquisition_price": 1000, "acquisition_shipping": 100, "acquisition_fees": 0,
               "sold_price": 2000, "selling_fee": 200, "outbound_shipping": 100}
    evidence = []
    for kind in (*amounts, "authenticity", "condition", "returns", "stop_loss"):
        evidence.append({"evidence_id": kind, "kind": kind, "source": "fixture",
                         "source_url": "https://example.com/" + kind, "observed_at": NOW,
                         "product_identity": deepcopy(IDENTITY), "amount": amounts.get(kind),
                         "assessment": "verified"})
    sold = deepcopy(evidence[3])
    sold.update(evidence_id="sold-2", source_url="https://example.com/sold-2")
    evidence.append(sold)
    assessment = {"candidate_id": "candidate-001", "product_identity": deepcopy(IDENTITY),
                  "source_url": "https://example.com/acquisition_price", "observed_at": NOW,
                  "acquisition_shipping": 100, "acquisition_fees": 0,
                  "expected_selling_fee": 200, "expected_outbound_shipping": 100,
                  "evidence": evidence, "strategy": "fixture-only", "condition_risk": "low",
                  "authenticity_risk": "low", "return_conditions": "verified",
                  "sellability": "supported", "stop_loss_price": 900, "max_hold_days": 10}
    return candidate, assessment


def shadow_fixture(repo=None):
    candidate, assessment = fixture()
    repo = repo or InMemoryShadowRepository()
    shadow = create_shadow_candidate(candidate, assessment, repository=repo, as_of=NOW)
    return repo, shadow


def observation_fixture(shadow, *, at=LATER):
    return {"observed_at": at, "source_price": 1000, "market_price": 2000,
            "estimated_sale_price": 2000, "active_listing_count": 3,
            "sold_evidence_count": 2, "liquidity_score": 0.8, "condition_changes": False,
            "stock_status": "available", "product_identity": deepcopy(IDENTITY),
            "evidence": deepcopy(shadow["evidence"])}


class ShadowPromotionTests(unittest.TestCase):
    def test_generate_observe_complete_and_promote(self):
        repo, shadow = shadow_fixture()
        self.assertFalse(shadow["external_execution_authorized"])
        self.assertEqual(shadow["expected_net_profit"], 600)
        observation = {"observed_at": LATER, "source_price": 1000, "market_price": 2000,
                       "estimated_sale_price": 2000, "active_listing_count": 3,
                       "sold_evidence_count": 2, "liquidity_score": 0.8,
                       "condition_changes": False, "stock_status": "available",
                       "product_identity": deepcopy(IDENTITY), "evidence": deepcopy(shadow["evidence"])}
        add_shadow_observation(repo, shadow["shadow_candidate_id"], observation, as_of=LATER)
        outcome = complete_shadow(repo, shadow["shadow_candidate_id"], as_of=LATER)
        self.assertEqual(outcome["outcome_status"], "success")
        self.assertEqual(outcome["hypothetical_profit"], 600)
        decision = evaluate_promotion(repo.get(shadow["shadow_candidate_id"]), as_of=LATER)
        self.assertTrue(decision["promotion_ready"])
        self.assertTrue(decision["human_review_ready"])
        self.assertTrue(decision["human_gate_required"])
        self.assertFalse(decision["purchase_authorized"])
        self.assertFalse(decision["external_execution_authorized"])

    def test_missing_evidence_high_profit_is_hold(self):
        candidate, assessment = fixture()
        candidate["expected_sale_price"] = 1000000
        assessment["evidence"] = []
        repo = InMemoryShadowRepository()
        shadow = create_shadow_candidate(candidate, assessment, repository=repo, as_of=NOW)
        decision = evaluate_promotion(shadow, as_of=NOW)
        self.assertFalse(decision["promotion_ready"])
        self.assertEqual(decision["status"], "research_usable_not_promotion_ready")
        outcome = complete_shadow(repo, shadow["shadow_candidate_id"], as_of=LATER)
        self.assertEqual(outcome["outcome_status"], "insufficient_evidence")

    def test_integrity_and_risks_fail_closed(self):
        for field, value, reason in (("liquidity_score", 0.1, "insufficient_liquidity"),
                                     ("condition_risk", "unknown", "condition_risk_unresolved"),
                                     ("authenticity_risk", "high", "authenticity_risk_unresolved"),
                                     ("return_conditions", None, "return_conditions_unverified"),
                                     ("stop_loss_price", None, "stop_loss_not_defined")):
            _, shadow = shadow_fixture()
            shadow[field] = value
            result = evaluate_promotion(shadow, as_of=NOW)
            self.assertIn(reason, result["reasons"])
            self.assertFalse(result["promotion_ready"])
        for change in ("edition", "stale", "future", "listing", "duplicate", "missing_url", "nan"):
            _, shadow = shadow_fixture()
            if change == "edition":
                shadow["evidence"][3]["product_identity"]["edition"] = "other"
            elif change == "stale":
                shadow["evidence"][3]["observed_at"] = "2020-01-01T00:00:00Z"
            elif change == "future":
                shadow["evidence"][3]["observed_at"] = LATER
            elif change == "listing":
                for row in shadow["evidence"]:
                    if row["kind"] == "sold_price":
                        row["kind"] = "listing_price"
            elif change == "duplicate":
                shadow["evidence"][-1]["source_url"] = shadow["evidence"][3]["source_url"]
            elif change == "missing_url":
                shadow["evidence"][0]["source_url"] = ""
            else:
                shadow["evidence"][0]["amount"] = float("nan")
            self.assertFalse(evaluate_promotion(shadow, as_of=NOW)["promotion_ready"], change)

    def test_snapshot_is_immutable_and_observation_cannot_execute(self):
        repo, shadow = shadow_fixture()
        shadow["acquisition_price"] = 9999
        saved = repo.get(shadow["shadow_candidate_id"])
        self.assertEqual(saved["acquisition_price"], 1000)
        with self.assertRaises(ValueError):
            add_shadow_observation(repo, saved["shadow_candidate_id"], {"observed_at": LATER,
                                   "external_execution_authorized": True}, as_of=LATER)

    def test_later_market_changes_block_promotion(self):
        for change in ("liquidity", "source_price", "source_unavailable", "sale_price"):
            repo, shadow = shadow_fixture()
            observation = observation_fixture(shadow)
            if change == "liquidity":
                observation["liquidity_score"] = 0.1
            elif change == "source_price":
                observation["source_price"] = 1200
            elif change == "source_unavailable":
                observation["stock_status"] = "unavailable"
            else:
                observation["estimated_sale_price"] = 1700
            key = shadow["shadow_candidate_id"]
            add_shadow_observation(repo, key, observation, as_of=LATER)
            complete_shadow(repo, key, as_of=LATER)
            # 1700 still yields minimum 300 profit; use higher minimum in that case.
            decision = evaluate_promotion(repo.get(key), as_of=LATER, min_net_profit=400)
            self.assertFalse(decision["promotion_ready"], change)

    def test_loss_and_identity_invalidation(self):
        for changed_identity in (False, True):
            repo, shadow = shadow_fixture()
            observation = observation_fixture(shadow)
            observation["estimated_sale_price"] = 1000
            if changed_identity:
                observation["product_identity"]["edition"] = "other"
            key = shadow["shadow_candidate_id"]
            add_shadow_observation(repo, key, observation, as_of=LATER)
            outcome = complete_shadow(repo, key, as_of=LATER)
            self.assertEqual(outcome["outcome_status"], "invalidated" if changed_identity else "loss")
            if not changed_identity:
                self.assertEqual(outcome["hypothetical_loss"], 400)
            self.assertFalse(evaluate_promotion(repo.get(key), as_of=LATER)["promotion_ready"])

    def test_bad_observations_and_malformed_evidence_are_closed(self):
        repo, shadow = shadow_fixture()
        for at in (NOW, "2026-10-07T00:00:00Z", "no-timezone"):
            with self.assertRaises(ValueError):
                add_shadow_observation(repo, shadow["shadow_candidate_id"], observation_fixture(shadow, at=at), as_of=LATER)
        shadow["evidence"][0]["kind"] = []
        self.assertFalse(evaluate_promotion(shadow, as_of=NOW)["promotion_ready"])
        candidate, assessment = fixture()
        with self.assertRaises(ValueError):
            create_shadow_candidate(candidate, assessment, repository=repo, as_of=NOW, maturity_stage="live_readiness")
        candidate["purchase_price"] = float("nan")
        with self.assertRaises(ValueError):
            create_shadow_candidate(candidate, assessment, repository=repo, as_of=NOW)

    def test_unsold_and_insufficient_observation(self):
        for unsold in (False, True):
            repo, shadow = shadow_fixture()
            at = "2026-10-16T00:00:00Z" if unsold else LATER
            observation = observation_fixture(shadow, at=at)
            observation["evidence"] = [row for row in observation["evidence"] if row["kind"] != "sold_price"]
            for row in observation["evidence"]:
                row["observed_at"] = at
            observation["sold_evidence_count"] = 0
            if unsold:
                observation["sellability_result"] = "unsold"
            key = shadow["shadow_candidate_id"]
            add_shadow_observation(repo, key, observation, as_of=at)
            outcome = complete_shadow(repo, key, as_of=at)
            self.assertEqual(outcome["outcome_status"], "unsold" if unsold else "insufficient_evidence")
            self.assertIsNone(outcome["hypothetical_profit"])

    def test_identity_fields_duplicate_tracking_urls_and_freshness_boundary(self):
        from research_lab.evidence_integrity import evaluate_integrity
        for field, value in (("model", "other"), ("jan", "other"), ("included_items", []), ("condition", "damaged")):
            _, shadow = shadow_fixture()
            shadow["evidence"][3]["product_identity"][field] = value
            self.assertFalse(evaluate_integrity(shadow, as_of=NOW)["passed"])
        _, shadow = shadow_fixture()
        self.assertTrue(evaluate_integrity(shadow, as_of="2026-10-12T00:00:00Z")["passed"])
        self.assertFalse(evaluate_integrity(shadow, as_of="2026-10-12T00:00:01Z")["passed"])
        shadow["evidence"][-1]["source_url"] = shadow["evidence"][3]["source_url"] + "?tracking=other#fragment"
        self.assertIn("duplicate_evidence", evaluate_integrity(shadow, as_of=NOW)["reasons"])
        candidate, assessment = fixture()
        candidate["metadata"]["product_id"] = "other"
        with self.assertRaises(ValueError):
            create_shadow_candidate(candidate, assessment, repository=InMemoryShadowRepository(), as_of=NOW)


def main():
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(ShadowPromotionTests))
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
