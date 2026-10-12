from __future__ import annotations

from .burn_in import assess_burn_in
from .human_gate import verify_human_approval
from .live_guard import authorize_action
from .orchestrator import run_orchestrator
from .preflight import run_preflight
from .release import build_release_status


def _candidate(key: str, supplier: str, supplier_cost: float) -> dict:
    return {
        "product_key": key,
        "name": f"proof-{key}",
        "category": "general",
        "supplier": supplier,
        "source": "v2-proof-fixture",
        "observed_at": "2026-10-11T04:00:00+00:00",
        "sale_price": 3000,
        "supplier_cost": supplier_cost,
        "supplier_shipping": 200,
        "platform_fee_rate": 0.10,
        "payment_fee_rate": 0.035,
        "ad_cost": 150,
        "expected_return_cost": 80,
        "refund_reserve": 100,
        "supplier_allows_dropshipping": True,
        "platform_terms_confirmed": True,
        "supplier_reliable": True,
        "inventory_confirmed": True,
        "delivery_days": 5,
    }


def build_v2_proof() -> dict:
    batches = [
        [_candidate("a", "supplier-a", 1500), _candidate("b", "supplier-b", 1100)],
        [_candidate("c", "supplier-a", 1400), _candidate("d", "supplier-b", 1000)],
        [_candidate("e", "supplier-a", 1300), _candidate("f", "supplier-b", 900)],
    ]
    orchestration = run_orchestrator(
        batches,
        available_capital=3000,
        strategy="balanced",
        state={
            "shadow_observations": 20,
            "shadow_days": 30,
            "sandbox_cycles": 10,
            "walk_forward_windows": 3,
            "evidence_integrity_passed": True,
            "ready_for_human_gate": True,
        },
    )
    preflight = run_preflight(
        batches[0][1],
        available_capital=3000,
        max_age_hours=99999,
    )
    live_write = authorize_action("submit_supplier_order")
    approval = verify_human_approval("8888")
    burn_in = assess_burn_in({
        "cycles": 20,
        "failure_rate": 0.01,
        "duplicate_orders": 0,
        "policy_violations": 0,
        "unhandled_errors": 0,
        "median_net_profit": 100,
    })
    checks = {
        "orchestrator_complete": orchestration["status"] == "orchestration_complete",
        "controller_completed": orchestration["controller"].get("status") == "completed",
        "single_item_selected": orchestration["controller"].get("selection", {}).get("one_item_only") is True,
        "strategy_experiment_ready": orchestration["strategy_experiment"].get("recommended_strategy") is not None,
        "preflight_passed": preflight["passed"] is True,
        "live_write_blocked": live_write["allowed"] is False,
        "approval_does_not_enable_live": approval["approved"] is True and approval["live_execution_allowed"] is False,
        "burn_in_does_not_auto_enable": burn_in["passed"] is True and burn_in["controlled_automation_allowed"] is False,
        "snapshot_append_only": orchestration["snapshot"]["append_only_intent"] is True,
        "no_external_writes": orchestration["external_writes"] is False,
    }
    return {
        "proof_version": "2.0",
        "passed": all(checks.values()),
        "checks": checks,
        "orchestration": orchestration,
        "preflight": preflight,
        "release": build_release_status(),
        "live_execution_allowed": False,
    }


def build_v2_acceptance() -> dict:
    proof = build_v2_proof()
    release = build_release_status()
    checks = {
        "proof_passed": proof["passed"],
        "research_release_ready": release["status"] == "research_endpoint_reached",
        "maturity_ceiling_human_gate": release["maturity_ceiling"] == "ready_for_human_gate",
        "live_commerce_disabled": release["capabilities"]["live_commerce_enabled"] is False,
        "live_execution_disabled": release["live_execution_allowed"] is False,
    }
    return {
        "acceptance_version": "2.0",
        "passed": all(checks.values()),
        "checks": checks,
        "release": release,
        "live_execution_allowed": False,
    }
