from __future__ import annotations

from .controller import run_controller
from .dashboard import build_dashboard_summary
from .research_plan import build_next_research_plan
from .snapshot import build_research_snapshot
from .strategy_experiment import compare_strategies


def run_orchestrator(
    batches: list[list[dict]],
    *,
    available_capital: float = 3000.0,
    strategy: str = "balanced",
    state: dict | None = None,
) -> dict:
    state = dict(state or {})
    first_batch = batches[0] if batches else []

    controller = run_controller(
        first_batch,
        strategy=strategy,
        available_capital=available_capital,
    ) if first_batch else {
        "status": "blocked",
        "stage": "selection",
        "live_execution_allowed": False,
    }

    experiment = compare_strategies(
        batches,
        available_capital=available_capital,
    ) if batches else {
        "status": "ok",
        "recommended_strategy": None,
        "strategies": [],
        "live_execution_allowed": False,
    }

    dashboard_state = {
        "version": "2.0",
        "candidate_count": sum(len(batch) for batch in batches),
        "eligible_count": (controller.get("ranking") or {}).get("eligible_count", 0),
        "shadow_observations": int(state.get("shadow_observations") or 0),
        "shadow_days": int(state.get("shadow_days") or 0),
        "sandbox_cycles": int(state.get("sandbox_cycles") or 0),
        "ready_for_human_gate": state.get("ready_for_human_gate") is True,
        "estimated_net_profit": float(controller.get("expected_net_profit") or 0),
    }
    dashboard = build_dashboard_summary(dashboard_state)

    plan = build_next_research_plan({
        "eligible_candidates": dashboard["eligible_count"],
        "shadow_days": dashboard["shadow_days"],
        "walk_forward_windows": int(state.get("walk_forward_windows") or 0),
        "sandbox_cycles": dashboard["sandbox_cycles"],
        "evidence_integrity_passed": state.get("evidence_integrity_passed") is True,
    })

    snapshot = build_research_snapshot({
        "maturity_stage": dashboard["maturity"]["stage"],
        "candidate_count": dashboard["candidate_count"],
        "eligible_count": dashboard["eligible_count"],
        "shadow_observations": dashboard["shadow_observations"],
        "shadow_days": dashboard["shadow_days"],
        "sandbox_cycles": dashboard["sandbox_cycles"],
        "selected_product_key": controller.get("selected_product_key"),
        "estimated_net_profit": controller.get("expected_net_profit") or 0,
    })

    return {
        "status": "orchestration_complete",
        "controller": controller,
        "strategy_experiment": experiment,
        "dashboard": dashboard,
        "research_plan": plan,
        "snapshot": snapshot,
        "external_writes": False,
        "live_execution_allowed": False,
        "human_gate_required_for_live": True,
    }
