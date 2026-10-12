from __future__ import annotations

from .controller import run_controller
from .live_guard import authorize_action
from .readiness import assess_live_readiness


def _fixture_offers() -> list[dict]:
    common = {
        "category": "general",
        "name": "proof-product",
        "source": "proof-fixture",
        "sale_price": 3000,
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
    return [
        common | {"product_key": "proof-a", "supplier": "supplier-a", "supplier_cost": 1500},
        common | {"product_key": "proof-b", "supplier": "supplier-b", "supplier_cost": 1100},
    ]


def build_proof() -> dict:
    controller = run_controller(_fixture_offers(), strategy="balanced", available_capital=3000)
    write_guard = authorize_action("submit_supplier_order")
    read_guard = authorize_action("fetch_inventory")
    passed = (
        controller.get("status") == "completed"
        and controller.get("external_writes") is False
        and controller.get("live_execution_allowed") is False
        and write_guard["allowed"] is False
        and read_guard["allowed"] is True
    )
    return {
        "proof_version": "0.9",
        "passed": passed,
        "controller": controller,
        "guards": {
            "read_allowed": read_guard,
            "live_write_blocked": write_guard,
        },
    }


def build_acceptance() -> dict:
    proof = build_proof()
    readiness = assess_live_readiness({
        "shadow_observations": 20,
        "shadow_days": 30,
        "sandbox_cycles": 10,
        "evidence_integrity_passed": True,
        "promotion_gate_passed": True,
        "duplicate_order_guard": True,
        "kill_switch_ready": True,
        "audit_log_ready": True,
        "external_writes_enabled": False,
    })
    checks = {
        "proof_passed": proof["passed"],
        "sandbox_completed": proof["controller"].get("status") == "completed",
        "one_item_selected": proof["controller"].get("selection", {}).get("selected") is not None,
        "live_write_blocked": proof["guards"]["live_write_blocked"]["allowed"] is False,
        "readiness_stops_at_human_gate": readiness["status"] == "ready_for_human_gate"
        and readiness["live_execution_allowed"] is False,
    }
    return {
        "acceptance_version": "0.9",
        "passed": all(checks.values()),
        "checks": checks,
        "readiness": readiness,
        "live_execution_allowed": False,
    }
