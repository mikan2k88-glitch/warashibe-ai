from __future__ import annotations

from .v52_proof import build_v52_proof
from .v53_sandbox_controller import run_v53_sandbox_cycle


def build_v53_proof() -> dict:
    v52 = build_v52_proof()
    review = v52["review"]

    delivered = run_v53_sandbox_cycle(review, scenario="delivered")
    cancelled = run_v53_sandbox_cycle(review, scenario="cancelled")
    failed = run_v53_sandbox_cycle(review, scenario="supplier_failure")
    refunded = run_v53_sandbox_cycle(review, scenario="refunded")
    delayed = run_v53_sandbox_cycle(review, scenario="delayed")

    checks = {
        "v52_proof_passed": v52["passed"] is True,
        "delivered_cycle_completed": delivered["sandbox_cycle_complete"] is True,
        "delivered_settled": delivered["settlement"]["status"] == "settled_sandbox",
        "cancelled_cycle_completed": cancelled["sandbox_cycle_complete"] is True,
        "supplier_failure_cycle_completed": failed["sandbox_cycle_complete"] is True,
        "refund_cycle_completed": refunded["sandbox_cycle_complete"] is True,
        "delay_remains_open": delayed["sandbox_cycle_complete"] is False and delayed["status"] == "in_progress",
        "outcome_created": delivered["outcome"]["mode"] == "sandbox_v53",
        "no_real_listing": delivered["real_listing_created"] is False,
        "no_real_supplier_order": delivered["real_supplier_order_created"] is False,
        "no_real_payment": delivered["real_payment_captured"] is False,
        "no_commerce_external_writes": delivered["commerce_external_writes"] is False,
        "live_execution_disabled": delivered["live_execution_allowed"] is False,
    }

    return {
        "proof_version": "5.3",
        "passed": all(checks.values()),
        "checks": checks,
        "delivered": delivered,
        "cancelled": cancelled,
        "supplier_failure": failed,
        "refunded": refunded,
        "delayed": delayed,
        "maturity_ceiling": "sandbox_commerce_validated",
        "live_execution_allowed": False,
    }


def build_v53_acceptance() -> dict:
    proof = build_v53_proof()
    checks = {
        "proof_passed": proof["passed"],
        "happy_path_settled": proof["delivered"]["settlement"]["status"] == "settled_sandbox",
        "refund_path_proven": proof["refunded"]["settlement"]["status"] == "refunded_sandbox",
        "cancel_path_proven": proof["cancelled"]["settlement"]["status"] == "cancelled_sandbox",
        "supplier_failure_path_proven": proof["supplier_failure"]["settlement"]["status"] == "cancelled_sandbox",
        "delayed_path_stays_open": proof["delayed"]["status"] == "in_progress",
        "live_execution_disabled": proof["live_execution_allowed"] is False,
    }
    return {
        "acceptance_version": "5.3",
        "passed": all(checks.values()),
        "checks": checks,
        "endpoint": "sandbox_commerce_validated",
        "next_phase": "live_readiness_and_limited_live_preparation",
        "live_execution_allowed": False,
    }
