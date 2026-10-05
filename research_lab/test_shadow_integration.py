"""Offline persistent routing, HQ and Dashboard agreement regressions."""
from copy import deepcopy
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app import app
from candidate_pipeline import evaluate_candidates
from research_lab.headquarters import build_headquarters_snapshot
from research_lab.hq_dashboard import build_hq_dashboard_payload
from research_lab.shadow_repository import JsonShadowRepository
from research_lab.shadow_state import build_validation_snapshot
from research_lab.shadow_validation import add_shadow_observation, complete_shadow
from research_lab.test_shadow_promotion import fixture, shadow_fixture, NOW, LATER, IDENTITY


class IntegrationTests(unittest.TestCase):
    def test_repository_reload_and_dashboard_agree(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "shadow.json"
            repo, shadow = shadow_fixture(JsonShadowRepository(path))
            key = shadow["shadow_candidate_id"]
            observation = {"observed_at": LATER, "source_price": 1000, "market_price": 2000,
                           "estimated_sale_price": 2000, "active_listing_count": 3,
                           "sold_evidence_count": 2, "liquidity_score": 0.8, "condition_changes": False,
                           "stock_status": "available", "product_identity": deepcopy(IDENTITY),
                           "evidence": deepcopy(shadow["evidence"])}
            add_shadow_observation(repo, key, observation, as_of=LATER)
            complete_shadow(repo, key, as_of=LATER)
            repo = JsonShadowRepository(path)
            snapshot = build_validation_snapshot(repository=repo, maturity_stage="shadow", as_of=LATER)
            self.assertEqual(snapshot["promotion_ready_count"], 1)
            self.assertEqual(snapshot["shadow_completed_count"], 1)
            self.assertEqual(len(repo.observations(key)), 1)
            hq = build_headquarters_snapshot(north_star="fixture", priority_order=["P2"],
                                            current_state={}, current_bottleneck="fixture", active_strategy=["fixture"],
                                            human_gate_required=False, evidence={}, observed_at=LATER,
                                            shadow_repository=repo, maturity_stage="shadow")
            dashboard = build_hq_dashboard_payload(shadow_repository=repo, maturity_stage="shadow", as_of=LATER)
            for field, value in snapshot.items():
                self.assertEqual(hq[field], value)
                self.assertEqual(dashboard[field], value)
                self.assertEqual(dashboard["hq_program"]["validation_state"][field], value)
            with patch.dict(os.environ, {"WARASHIBE_SHADOW_STORE": str(path), "WARASHIBE_MATURITY_STAGE": "shadow"}):
                payload = app.test_client().get("/hq/api").get_json()
                html = app.test_client().get("/hq").get_data(as_text=True)
            self.assertEqual(payload["shadow_completed_count"], 1)
            self.assertIn("Shadow完了数</span><b>1</b>", html)
            self.assertIn("Maturity Stage</span><b>shadow</b>", html)
            self.assertTrue(payload["human_gate_required"])
            self.assertFalse(payload["external_execution_authorized"])

    def test_opt_in_preserves_p2_selection(self):
        from research_lab.shadow_repository import InMemoryShadowRepository
        candidate, assessment = fixture()
        # Keep the existing whole-capital one-item rule and confidence gate.
        candidate["confidence"] = 0.9
        legacy = evaluate_candidates([candidate], 1000)
        repo = InMemoryShadowRepository()
        routed = evaluate_candidates([candidate], 1000, shadow_repository=repo,
                                     shadow_assessment=assessment, as_of=NOW)
        self.assertNotIn("shadow_routing", legacy)
        self.assertEqual({k: v for k, v in routed.items() if k != "shadow_routing"}, legacy)
        self.assertEqual(routed["shadow_routing"]["status"], "shadow_candidate")
        self.assertEqual(len(repo.load()), 1)

    def test_repository_corruption_and_reopen_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "shadow.json"
            path.write_text("broken", encoding="utf-8")
            with self.assertRaises(ValueError):
                JsonShadowRepository(path)
        repo, shadow = shadow_fixture()
        complete_shadow(repo, shadow["shadow_candidate_id"], as_of=LATER)
        with self.assertRaises(ValueError):
            repo.finish(shadow["shadow_candidate_id"], repo.get(shadow["shadow_candidate_id"])["outcome"])

    def test_atomic_write_failure_rolls_back(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "shadow.json"
            repo, shadow = shadow_fixture(JsonShadowRepository(path))
            saved = path.read_bytes()
            candidate, assessment = fixture()
            with patch("research_lab.shadow_repository.os.replace", side_effect=OSError("fixture write failure")):
                with self.assertRaises(OSError):
                    from research_lab.shadow_validation import create_shadow_candidate
                    create_shadow_candidate(candidate, assessment, repository=repo, as_of=NOW)
            self.assertEqual(len(repo.load()), 1)
            self.assertEqual(path.read_bytes(), saved)
            self.assertEqual(list(Path(directory).glob("*.tmp")), [])

    def test_cli_runs_local_loop_without_commerce(self):
        import contextlib
        import io
        import json
        from research_lab.shadow_cli import main as run_cli
        from research_lab.test_shadow_promotion import observation_fixture
        with tempfile.TemporaryDirectory() as directory:
            store = Path(directory) / "shadow.json"
            packet = Path(directory) / "input.json"
            candidate, assessment = fixture()
            packet.write_text(json.dumps({"candidate": candidate, "assessment": assessment}), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                shadow = run_cli(["candidate", "--store", str(store), "--as-of", NOW, "--input", str(packet)])
                packet.write_text(json.dumps(observation_fixture(shadow)), encoding="utf-8")
                common = ["--store", str(store), "--as-of", LATER, "--id", shadow["shadow_candidate_id"]]
                run_cli(["observe", *common, "--input", str(packet)])
                outcome = run_cli(["outcome", *common])
                snapshot = run_cli(["snapshot", "--store", str(store), "--as-of", LATER])
            self.assertEqual(snapshot["promotion_ready_count"], 1)
            self.assertFalse(outcome["external_execution_authorized"])


def main():
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(IntegrationTests))
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
