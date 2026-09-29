"""Offline regression suite for research_lab.sale_evidence_join_gate."""
import unittest
from copy import deepcopy
from research_lab.sale_evidence_join_gate import review_sale_evidence_join


_UNSET = object()


class TestSaleEvidenceJoinGate(unittest.TestCase):
    def setUp(self):
        self.listing = dict(item_id="item-001", marketplace="ebay", evidence_ref="listing:001",
                            source="ebay_browse", observed_at="2026-09-25T09:00:00+09:00",
                            asking_price_only=True)
        self.sale = dict(item_id="item-001", marketplace="ebay", evidence_ref="sale:001",
                         source="independent_sales_dataset", observed_at="2026-09-26T09:00:00+09:00")
        self.as_of = "2026-09-29T09:00:00+09:00"

    def review(self, listing=_UNSET, sale=_UNSET, **kwargs):
        return review_sale_evidence_join(self.listing if listing is _UNSET else listing,
                                         self.sale if sale is _UNSET else sale,
                                         as_of=kwargs.pop("as_of", self.as_of), **kwargs)

    def assert_hold(self, result, reason):
        self.assertEqual(result["status"], "hold_evidence_join")
        self.assertIn(reason, result["reasons"])
        self.assertIs(result["join_reviewable"], False)
        self.assertIsNone(result["scenario"])
        self.assertIs(result["external_action_authorized"], False)
        self.assertIs(result["asking_price_only"], True)

    def test_matching_independent_evidence_is_only_reviewable(self):
        result = self.review()
        self.assertEqual(result["status"], "reviewable_provenance_pair")
        self.assertIs(result["join_reviewable"], True)
        self.assertIsNone(result["scenario"])
        self.assertIs(result["external_action_authorized"], False)
        self.assertIs(result["asking_price_only"], True)

    def test_identity_mismatch(self):
        for field, value in (("item_id", "item-002"), ("marketplace", "other_market")):
            with self.subTest(field=field):
                changed = deepcopy(self.sale)
                changed[field] = value
                self.assert_hold(self.review(sale=changed), "different_item_or_marketplace")

    def test_evidence_independence(self):
        for field, value in (("evidence_ref", "listing:001"), ("source", "ebay_browse")):
            with self.subTest(field=field):
                changed = deepcopy(self.sale)
                changed[field] = value
                self.assert_hold(self.review(sale=changed), "sale_evidence_not_independent")

    def test_missing_identity_or_provenance(self):
        for field in ("item_id", "marketplace", "evidence_ref", "source", "observed_at"):
            with self.subTest(field=field):
                changed = deepcopy(self.sale)
                changed[field] = ""
                self.assert_hold(self.review(sale=changed), "sale_missing_identity_or_provenance")

    def test_malformed_or_stale_times(self):
        for timestamp in ("2026-09-30T00:00:00+09:00", "2026-09-01T09:00:00+09:00",
                          "2026-09-26T09:00:00", "not-a-date"):
            with self.subTest(timestamp=timestamp):
                changed = deepcopy(self.sale)
                changed["observed_at"] = timestamp
                self.assert_hold(self.review(sale=changed), "sale_invalid_or_stale_time")

    def test_seven_day_boundary_is_inclusive(self):
        changed = deepcopy(self.sale)
        changed["observed_at"] = "2026-09-22T09:00:00+09:00"
        self.assertTrue(self.review(sale=changed)["join_reviewable"])

    def test_invalid_clock_and_max_age(self):
        self.assert_hold(self.review(as_of="2026-09-29T09:00:00"), "invalid_as_of")
        for value in (False, 0, -1, float("nan"), float("inf"), "7"):
            with self.subTest(value=value):
                self.assert_hold(self.review(max_age_days=value), "invalid_max_age")

    def test_listing_label_required(self):
        changed = deepcopy(self.listing)
        changed.pop("asking_price_only")
        self.assert_hold(self.review(listing=changed), "listing_must_remain_asking_price_only")

    def test_bad_inputs_fail_closed(self):
        for obj in (None, [], "x"):
            with self.subTest(obj=obj):
                self.assert_hold(self.review(listing=obj), "invalid_record")


if __name__ == "__main__":
    unittest.main()
