"""Offline regression tests for the sale evidence attestation review gate."""
import unittest
from copy import deepcopy

from research_lab.sale_evidence_attestation_gate import review_attested_sale_evidence


class TestSaleEvidenceAttestationGate(unittest.TestCase):
    def setUp(self):
        self.listing = dict(item_id="item-001", marketplace="ebay", evidence_ref="listing:001",
                            source="ebay_browse", observed_at="2026-09-25T09:00:00+09:00",
                            asking_price_only=True)
        self.sale = dict(item_id="item-001", marketplace="ebay", evidence_ref="sale:001",
                         source="independent_sales_dataset", observed_at="2026-09-26T09:00:00+09:00")
        self.attestation = dict(item_id="item-001", marketplace="ebay",
                                listing_evidence_ref="listing:001", sale_evidence_ref="sale:001",
                                verifier="independent_reviewer", verification_method="manual_record_review",
                                verification_ref="review:001", verified_at="2026-09-28T09:00:00+09:00",
                                verification_status="verified")
        self.as_of = "2026-09-29T09:00:00+09:00"

    def review(self, *, listing=None, sale=None, attestation=None, as_of=None, max_age_days=7):
        return review_attested_sale_evidence(
            self.listing if listing is None else listing,
            self.sale if sale is None else sale,
            self.attestation if attestation is None else attestation,
            as_of=self.as_of if as_of is None else as_of, max_age_days=max_age_days)

    def assert_safe(self, result):
        self.assertIsNone(result["scenario"])
        self.assertIs(result["external_action_authorized"], False)
        self.assertIs(result["asking_price_only"], True)

    def assert_hold(self, result, reason):
        self.assertEqual(result["status"], "hold_sale_attestation")
        self.assertIs(result["reviewable_attestation"], False)
        self.assertIn(reason, result["reasons"])
        self.assert_safe(result)

    def test_valid_record_only_becomes_reviewable(self):
        result = self.review()
        self.assertEqual(result["status"], "attestation_record_reviewable")
        self.assertIs(result["reviewable_attestation"], True)
        self.assertEqual(result["reasons"], ())
        self.assert_safe(result)

    def test_missing_or_incomplete_record_is_held(self):
        self.assert_hold(review_attested_sale_evidence(self.listing, self.sale, None, as_of=self.as_of),
                         "missing_attestation")
        for field in ("item_id", "marketplace", "listing_evidence_ref", "sale_evidence_ref",
                      "verifier", "verification_method", "verification_ref", "verified_at"):
            with self.subTest(field=field):
                record = deepcopy(self.attestation)
                record[field] = ""
                self.assert_hold(self.review(attestation=record), "incomplete_attestation")

    def test_identity_and_references_must_match(self):
        for field, value in (("item_id", "item-002"), ("marketplace", "other_market"),
                             ("listing_evidence_ref", "listing:other"),
                             ("sale_evidence_ref", "sale:other")):
            with self.subTest(field=field):
                record = deepcopy(self.attestation)
                record[field] = value
                self.assert_hold(self.review(attestation=record), "attestation_identity_mismatch")

    def test_verifier_and_review_reference_must_be_independent(self):
        for field, value in (("verifier", "ebay_browse"),
                             ("verifier", "independent_sales_dataset"),
                             ("verification_ref", "listing:001"),
                             ("verification_ref", "sale:001")):
            with self.subTest(field=field, value=value):
                record = deepcopy(self.attestation)
                record[field] = value
                self.assert_hold(self.review(attestation=record), "attestation_not_independent")

    def test_explicit_verification_status_required(self):
        for value in (None, "pending", "rejected", ""):
            with self.subTest(value=value):
                record = deepcopy(self.attestation)
                record["verification_status"] = value
                self.assert_hold(self.review(attestation=record), "verification_not_confirmed")

    def test_invalid_future_or_stale_verification_time(self):
        for value in ("2026-09-30T09:00:00+09:00", "2026-09-20T09:00:00+09:00",
                      "2026-09-28T09:00:00", "not-a-date"):
            with self.subTest(value=value):
                record = deepcopy(self.attestation)
                record["verified_at"] = value
                self.assert_hold(self.review(attestation=record), "invalid_or_stale_verification_time")

    def test_seven_day_boundary_is_inclusive(self):
        record = deepcopy(self.attestation)
        record["verified_at"] = "2026-09-22T09:00:00+09:00"
        result = self.review(attestation=record)
        self.assertIs(result["reviewable_attestation"], True)
        self.assert_safe(result)

    def test_invalid_review_clock_or_max_age_is_held(self):
        self.assert_hold(self.review(as_of="2026-09-29T09:00:00"),
                         "provenance_pair_not_reviewable")
        for value in (False, 0, -1, float("nan"), float("inf"), "7"):
            with self.subTest(value=value):
                self.assert_hold(self.review(max_age_days=value), "provenance_pair_not_reviewable")

    def test_unreviewable_provenance_never_bypassed(self):
        bad_sale = deepcopy(self.sale)
        bad_sale["source"] = self.listing["source"]
        self.assert_hold(self.review(sale=bad_sale), "provenance_pair_not_reviewable")
        bad_listing = deepcopy(self.listing)
        bad_listing["asking_price_only"] = False
        self.assert_hold(self.review(listing=bad_listing), "provenance_pair_not_reviewable")


if __name__ == "__main__":
    unittest.main()
