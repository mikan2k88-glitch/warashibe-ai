"""Smoke tests for the research-lab control layer."""

from research_lab.director import ResearchSignal, choose_next_track, stage_complete
from research_lab.evaluator import Metrics, compare
from research_lab.report import build_summary


def run() -> None:
    signals = [
        ResearchSignal("route", 0.90, 0.3, 0.4),
        ResearchSignal("speed", 0.20, 0.9, 0.9),
        ResearchSignal("real_market", 0.05, 1.0, 1.0),
    ]
    assert choose_next_track(signals).track == "real_market"
    assert stage_complete(ResearchSignal("route", 0.95, 0.2, 0.2), 3, True)

    baseline = Metrics(0.40, 20.0, 100.0, True)
    faster = Metrics(0.40, 15.0, 100.0, True)
    assert compare(baseline, faster).status == "candidate"
    assert compare(baseline, Metrics(0.39, 10.0, 50.0, True)).status == "hold"
    assert compare(baseline, Metrics(0.50, 30.0, 120.0, False)).status == "reject"

    summary = build_summary(
        learned="control layer works",
        improved="automatic research triage",
        numbers="smoke tests passed",
        decision="continue research",
        maturity="foundation",
        next_theme="speed metrics",
        github_update=False,
    )
    assert "研究サマリー" in summary


if __name__ == "__main__":
    run()
    print("RESEARCH LAB: PASSED")
